import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from dotenv import load_dotenv # Đảm bảo bạn đã cài đặt: pip install python-dotenv

class GoogleDriveManager:
    """
    Một lớp để quản lý các thao tác với Google Drive sử dụng Service Account.
    """

    def __init__(self, folder_id: str ="", service_account_key_path: str = "", scopes: list = None):
        """
        Khởi tạo GoogleDriveManager.

        Args:
            folder_id (str, optional): ID của thư mục Google Drive mặc định để làm việc.
                                       Nếu không cung cấp, sẽ cố gắng đọc từ biến môi trường GOOGLE_DRIVE_FOLDER_ID.
            service_account_key_path (str, optional): Đường dẫn tới file JSON của Service Account Key.
                                                      Nếu không cung cấp, sẽ cố gắng đọc từ biến môi trường GOOGLE_SERVICE_ACCOUNT_KEY_PATH.
            scopes (list, optional): Danh sách các SCOPES API được yêu cầu. Mặc định là full drive access.
        """
        load_dotenv() # Tải các biến môi trường từ tệp .env

        # Lấy folder_id
        self.folder_id = folder_id if folder_id else os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        if not self.folder_id:
            raise ValueError("Google Drive FOLDER_ID phải được cung cấp hoặc định nghĩa trong biến môi trường GOOGLE_DRIVE_FOLDER_ID.")

        # Lấy đường dẫn tới file khóa Service Account JSON
        self.service_account_key_path = service_account_key_path \
                                        if service_account_key_path \
                                        else os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY_PATH')

        if not self.service_account_key_path:
            raise ValueError("Đường dẫn tới file Service Account Key JSON phải được cung cấp hoặc định nghĩa trong biến môi trường GOOGLE_SERVICE_ACCOUNT_KEY_PATH.")
        
        # Kiểm tra xem file có tồn tại không
        if not os.path.exists(self.service_account_key_path):
            raise FileNotFoundError(f"Không tìm thấy file Service Account Key tại đường dẫn: {self.service_account_key_path}")

        try:
            # Đọc nội dung file JSON
            with open(self.service_account_key_path, 'r') as f:
                self.service_account_info = json.load(f) # json.load() đọc trực tiếp từ file object
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Lỗi định dạng JSON trong file Service Account Key tại {self.service_account_key_path}. "
                f"Đảm bảo file là JSON hợp lệ. Lỗi: {e}"
            )
        except Exception as e:
            raise ValueError(f"Lỗi không mong muốn khi đọc file Service Account Key: {e}")

        # Định nghĩa các SCOPES
        self.scopes = scopes if scopes else ['https://www.googleapis.com/auth/drive']

        self.service = self._authenticate()

    def _authenticate(self):
        """
        Xác thực với Google Drive API bằng Service Account.

        Returns:
            googleapiclient.discovery.Resource: Đối tượng service đã xác thực.
        Raises:
            Exception: Nếu xác thực thất bại.
        """
        try:
            # Sử dụng đối tượng dictionary đã được parse từ __init__
            creds = service_account.Credentials.from_service_account_info(
                self.service_account_info, scopes=self.scopes
            )
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            raise Exception(f"Không thể xác thực với Google Drive: {e}")

    def upload_file(self, file_path: str, target_folder_id: str = None, mimetype: str = 'application/octet-stream'):
        """
        Tải lên một tệp lên Google Drive.

        Args:
            file_path (str): Đường dẫn đến tệp cục bộ cần tải lên.
            target_folder_id (str, optional): ID của thư mục đích trên Drive.
                                              Mặc định sẽ sử dụng self.folder_id.
            mimetype (str, optional): Loại MIME của tệp (ví dụ: 'text/plain', 'application/pdf').
                                      Mặc định là 'application/octet-stream' (dạng byte chung).
        Returns:
            str: ID của tệp đã tải lên trên Google Drive, hoặc None nếu thất bại.
        """
        if not os.path.exists(file_path):
            print(f"Lỗi: Tệp cục bộ không tồn tại tại đường dẫn: {file_path}")
            return None

        actual_target_folder_id = target_folder_id if target_folder_id else self.folder_id
        file_name = os.path.basename(file_path)
        file_metadata = {
            'name': file_name,
            'parents': [actual_target_folder_id]
        }

        media = MediaFileUpload(file_path, mimetype=mimetype, resumable=True)

        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name'
            ).execute()
            print(f"Tệp '{file.get('name')}' đã được tải lên với ID: {file.get('id')}")
            return file.get('id')
        except HttpError as error:
            print(f"Lỗi khi tải lên tệp '{file_name}': {error}")
        except Exception as e:
            print(f"Lỗi không mong muốn khi tải lên: {e}")
        return None

    def list_files(self, query: str = None, page_size: int = 10, fields: str = "nextPageToken, files(id, name)"):
        """
        Liệt kê các tệp trên Google Drive.

        Args:
            query (str, optional): Một truy vấn để lọc tệp (ví dụ: "'folder_id' in parents").
            page_size (int, optional): Số lượng tệp tối đa trả về mỗi trang.
            fields (str, optional): Các trường thông tin tệp muốn lấy.

        Returns:
            list: Danh sách các dict chứa thông tin tệp (id, name).
        """
        try:
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                fields=fields
            ).execute()
            items = results.get('files', [])
            if not items:
                print("Không tìm thấy tệp nào với truy vấn này.")
            return items
        except HttpError as error:
            print(f"Lỗi khi liệt kê tệp: {error}")
        except Exception as e:
            print(f"Lỗi không mong muốn khi liệt kê tệp: {e}")
        return []

    def create_folder(self, folder_name: str, parent_folder_id: str = None):
        """
        Tạo một thư mục mới trên Google Drive.

        Args:
            folder_name (str): Tên của thư mục mới.
            parent_folder_id (str, optional): ID của thư mục cha. Mặc định là self.folder_id.
        Returns:
            str: ID của thư mục mới được tạo, hoặc None nếu thất bại.
        """
        actual_parent_id = parent_folder_id if parent_folder_id else self.folder_id
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [actual_parent_id]
        }
        try:
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name'
            ).execute()
            print(f"Thư mục '{folder.get('name')}' đã được tạo với ID: {folder.get('id')}")
            return folder.get('id')
        except HttpError as error:
            print(f"Lỗi khi tạo thư mục '{folder_name}': {error}")
        except Exception as e:
            print(f"Lỗi không mong muốn khi tạo thư mục: {e}")
        return None

    def delete_file(self, file_id: str):
        """
        Xóa một tệp hoặc thư mục trên Google Drive.

        Args:
            file_id (str): ID của tệp hoặc thư mục cần xóa.
        Returns:
            bool: True nếu xóa thành công, False nếu thất bại.
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"Đã xóa tệp/thư mục với ID: {file_id}")
            return True
        except HttpError as error:
            print(f"Lỗi khi xóa tệp/thư mục '{file_id}': {error}")
        except Exception as e:
            print(f"Lỗi không mong muốn khi xóa: {e}")
        return False


# --- Cách sử dụng lớp GoogleDriveManager ---
if __name__ == "__main__":

    try:
        # Khởi tạo đối tượng quản lý Drive.
        # Nó sẽ tự động đọc FOLDER_ID và SERVICE_ACCOUNT_KEY_PATH từ .env
        drive_manager = GoogleDriveManager()

        print("\n--- Tải lên tệp ví dụ ---")
        example_file_name = "build_report_20250630.txt"
        with open(example_file_name, "w") as f:
            f.write("Báo cáo build CI/CD:\n")
            f.write("Trạng thái: THÀNH CÔNG\n")
            f.write("Thời gian: 2025-06-30 14:30:00\n")
            f.write("Các lỗi (nếu có): Không\n")

        uploaded_file_id = drive_manager.upload_file(example_file_name, mimetype='text/plain')
        if uploaded_file_id:
            print(f"Tệp đã được tải lên thành công: {uploaded_file_id}")
        
        # Dọn dẹp tệp ví dụ cục bộ
        if os.path.exists(example_file_name):
            os.remove(example_file_name)

        print("\n--- Liệt kê các tệp trong thư mục mặc định ---")
        files_in_folder = drive_manager.list_files(query=f"'{drive_manager.folder_id}' in parents", page_size=20)
        if files_in_folder:
            for item in files_in_folder:
                print(f"- {item['name']} (ID: {item['id']})")

    except (ValueError, FileNotFoundError) as e:
        print(f"Lỗi cấu hình hoặc file: {e}")
        print("Vui lòng đảm bảo biến GOOGLE_DRIVE_FOLDER_ID và GOOGLE_SERVICE_ACCOUNT_KEY_PATH được định nghĩa đúng cách trong tệp .env và file JSON Service Account Key tồn tại.")
    except Exception as e:
        print(f"Đã xảy ra lỗi chung: {e}")