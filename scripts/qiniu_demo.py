from qiniu import Auth, put_data, etag
import hashlib
from flask import current_app
from app import create_app


def generate_hash(file_obj):
    # 生成文件内容的哈希值
    md5_hash = hashlib.md5(file_obj)
    # 读取文件内容并计算哈希值
    # md5_hash.update(file_obj)
    # 返回哈希值的十六进制表示
    return md5_hash.hexdigest()


def uploadFile_test(file_obj):
    # 需要填写你的 Access Key 和 Secret Key
    access_key = current_app.config.get('QINIU_AK')
    secret_key = current_app.config.get('QINIU_SK')
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = current_app.config.get('QINIU_BUCKET')
    # 上传后保存的文件名(根据文件内容生成hash值作为文件名)
    key = 'flask/toutiao/' + generate_hash(file_obj)
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_data(token, key, file_obj)
    print(info)
    print(ret)


if __name__ == "__main__":
    app = create_app('dev')
    with app.app_context():
        # 现在可以使用 current_app 了
        with open('./2.webp', 'rb') as f:
            uploadFile_test(f.read())
