"""Script hỗ trợ kiểm tra và dọn dẹp tài nguyên AWS cho đồ án Cloud Photo (Tuần 4).

Nguyên tắc an toàn:
1. Mặc định chạy ở chế độ kiểm tra an toàn (Dry-run), chỉ liệt kê tài nguyên cần dọn.
2. Chỉ xóa tài nguyên khi có tham số --confirm.
3. Chỉ dọn dẹp các tài nguyên thuộc dự án Cloud Photo (có tên tương ứng).
4. Tuyệt đối không can thiệp vào các tài nguyên chung của AWS Academy (LabRole, LabInstanceProfile, default VPC).

Sử dụng:
  py -3.12 scripts/teardown_resources.py --dry-run
  py -3.12 scripts/teardown_resources.py --confirm
"""

import argparse
import sys
import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
EC2_NAME = "cloud-photo-gallery"
SG_NAME = "cloud-photo-web-sg"
BUCKET_INPUT = "cloudphoto-input-103308504802"
BUCKET_OUTPUT = "cloudphoto-output-103308504802"
LAMBDA_NAME = "cloud-photo-processor"
LAYER_NAME = "cloud-photo-pillow"
DYNAMODB_TABLE = "cloud-photo-metadata"
LOG_GROUP = "/aws/lambda/cloud-photo-processor"


def check_resources():
    print("=" * 60)
    print("KIỂM TRA TRẠNG THÁI TÀI NGUYÊN DỰ ÁN TRÊN AWS (us-east-1)")
    print("=" * 60)

    session = boto3.Session(region_name=REGION)
    ec2 = session.client("ec2")
    s3 = session.client("s3")
    lambda_client = session.client("lambda")
    dynamodb = session.client("dynamodb")
    logs = session.client("logs")

    # 1. EC2
    try:
        res = ec2.describe_instances(Filters=[{"Name": "tag:Name", "Values": [EC2_NAME]}])
        instances = [i for r in res.get("Reservations", []) for i in r.get("Instances", []) if i["State"]["Name"] != "terminated"]
        if instances:
            for inst in instances:
                print(f"[EC2] Tìm thấy instance: {inst['InstanceId']} ({inst['State']['Name']})")
        else:
            print("[EC2] Không có instance nào đang chạy (đã dọn dẹp).")
    except Exception as e:
        print(f"[EC2] Lỗi kiểm tra: {e}")

    # 2. S3
    for b_name in [BUCKET_INPUT, BUCKET_OUTPUT]:
        try:
            s3.head_bucket(Bucket=b_name)
            print(f"[S3] Bucket đang tồn tại: {b_name}")
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchBucket"):
                print(f"[S3] Bucket không tồn tại (đã dọn dẹp): {b_name}")
            else:
                print(f"[S3] Trạng thái bucket {b_name}: {e}")

    # 3. Lambda
    try:
        lambda_client.get_function(FunctionName=LAMBDA_NAME)
        print(f"[Lambda] Hàm đang tồn tại: {LAMBDA_NAME}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"[Lambda] Hàm không tồn tại (đã dọn dẹp): {LAMBDA_NAME}")
        else:
            print(f"[Lambda] Trạng thái hàm {LAMBDA_NAME}: {e}")

    # 4. DynamoDB
    try:
        tbl = dynamodb.describe_table(TableName=DYNAMODB_TABLE)
        print(f"[DynamoDB] Bảng đang tồn tại: {DYNAMODB_TABLE} ({tbl['Table']['TableStatus']})")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(f"[DynamoDB] Bảng không tồn tại (đã dọn dẹp): {DYNAMODB_TABLE}")
        else:
            print(f"[DynamoDB] Trạng thái bảng {DYNAMODB_TABLE}: {e}")

    # 5. CloudWatch Logs
    try:
        res = logs.describe_log_groups(logGroupNamePrefix=LOG_GROUP)
        found = [lg for lg in res.get("logGroups", []) if lg["logGroupName"] == LOG_GROUP]
        if found:
            print(f"[CloudWatch] Nhóm log đang tồn tại: {LOG_GROUP}")
        else:
            print(f"[CloudWatch] Nhóm log không tồn tại (đã dọn dẹp): {LOG_GROUP}")
    except Exception as e:
        print(f"[CloudWatch] Trạng thái log: {e}")

    print("=" * 60)


def empty_and_delete_bucket(s3_client, bucket_name):
    print(f"-> Đang làm rỗng và xóa bucket {bucket_name}...")
    try:
        # Xóa toàn bộ objects
        paginator = s3_client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket_name):
            if "Contents" in page:
                del_objects = [{"Key": obj["Key"]} for obj in page["Contents"]]
                s3_client.delete_objects(Bucket=bucket_name, Delete={"Objects": del_objects})
                print(f"   Đã xóa {len(del_objects)} objects trong {bucket_name}")

        # Xóa toàn bộ versions nếu có
        ver_paginator = s3_client.get_paginator("list_object_versions")
        for page in ver_paginator.paginate(Bucket=bucket_name):
            del_list = []
            for ver in page.get("Versions", []):
                del_list.append({"Key": ver["Key"], "VersionId": ver["VersionId"]})
            for dm in page.get("DeleteMarkers", []):
                del_list.append({"Key": dm["Key"], "VersionId": dm["VersionId"]})
            if del_list:
                s3_client.delete_objects(Bucket=bucket_name, Delete={"Objects": del_list})

        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"   [Thành công] Đã xóa bucket {bucket_name}")
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchBucket"):
            print(f"   Bucket {bucket_name} không tồn tại.")
        else:
            print(f"   [Cảnh báo] Lỗi khi xóa bucket {bucket_name}: {e}")


def execute_teardown():
    session = boto3.Session(region_name=REGION)
    ec2 = session.client("ec2")
    s3 = session.client("s3")
    lambda_client = session.client("lambda")
    dynamodb = session.client("dynamodb")
    logs = session.client("logs")

    print("\nBẮT ĐẦU QUY TRÌNH DỌN DẸP TÀI NGUYÊN...")

    # 1. Hủy Event Notification S3
    try:
        print("1. Hủy bỏ S3 Event Notification trên bucket input...")
        s3.put_bucket_notification_configuration(
            Bucket=BUCKET_INPUT,
            NotificationConfiguration={}
        )
        print("   [Thành công] Đã gỡ bỏ S3 Notification.")
    except Exception as e:
        print(f"   [Bỏ qua] {e}")

    # 2. Terminate EC2
    try:
        print(f"2. Terminate máy chủ EC2 ({EC2_NAME})...")
        res = ec2.describe_instances(Filters=[{"Name": "tag:Name", "Values": [EC2_NAME]}])
        instance_ids = [i["InstanceId"] for r in res.get("Reservations", []) for i in r.get("Instances", []) if i["State"]["Name"] != "terminated"]
        if instance_ids:
            ec2.terminate_instances(InstanceIds=instance_ids)
            print(f"   [Thành công] Đã gửi lệnh terminate tới {instance_ids}")
        else:
            print("   Không tìm thấy instance EC2 nào cần xóa.")
    except Exception as e:
        print(f"   [Lỗi EC2] {e}")

    # 3. Xóa Buckets S3
    print("3. Dọn dẹp S3 Buckets...")
    empty_and_delete_bucket(s3, BUCKET_INPUT)
    empty_and_delete_bucket(s3, BUCKET_OUTPUT)

    # 4. Xóa Lambda Function
    try:
        print(f"4. Xóa hàm Lambda {LAMBDA_NAME}...")
        lambda_client.delete_function(FunctionName=LAMBDA_NAME)
        print(f"   [Thành công] Đã xóa hàm Lambda {LAMBDA_NAME}")
    except ClientError as e:
        print(f"   [Bỏ qua] {e}")

    # 5. Xóa DynamoDB
    try:
        print(f"5. Xóa bảng DynamoDB {DYNAMODB_TABLE}...")
        dynamodb.delete_table(TableName=DYNAMODB_TABLE)
        print(f"   [Thành công] Đã xóa bảng {DYNAMODB_TABLE}")
    except ClientError as e:
        print(f"   [Bỏ qua] {e}")

    # 6. Xóa CloudWatch Logs
    try:
        print(f"6. Xóa nhóm log CloudWatch {LOG_GROUP}...")
        logs.delete_log_group(logGroupName=LOG_GROUP)
        print(f"   [Thành công] Đã xóa log group {LOG_GROUP}")
    except ClientError as e:
        print(f"   [Bỏ qua] {e}")

    print("\nHOÀN TẤT DỌN DẸP TÀI NGUYÊN.")


def main():
    parser = argparse.ArgumentParser(description="Dọn dẹp tài nguyên AWS cho đồ án Cloud Photo.")
    parser.add_argument("--dry-run", action="store_true", help="Kiểm tra trạng thái tài nguyên mà không xóa.")
    parser.add_argument("--confirm", action="store_true", help="Xác nhận tiến hành xóa tài nguyên.")

    args = parser.parse_args()

    if args.confirm:
        confirm = input("CẢNH BÁO: Bạn có chắc chắn muốn XÓA TOÀN BỘ tài nguyên của đồ án trên AWS? (yes/no): ")
        if confirm.lower() == "yes":
            execute_teardown()
            check_resources()
        else:
            print("Đã hủy bỏ thao tác xóa.")
    else:
        check_resources()
        print("\nGợi ý: Để tiến hành dọn dẹp sau khi quay xong video demo, chạy lệnh:")
        print("  py -3.12 scripts/teardown_resources.py --confirm")


if __name__ == "__main__":
    main()

