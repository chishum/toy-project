import os.path

from dirsync import sync

# 동기화할 원본 폴더와 대상 폴더의 경로를 지정합니다.
source_path = "/Users/chishum/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal"
target_path = "/Users/chishum/Library/CloudStorage/GoogleDrive-chishum9@gmail.com/내 드라이브/Obsidian/Personal"

if __name__ == '__main__':
    # sync 함수를 사용하여 폴더를 동기화합니다.
    # 'sync' 모드는 파일을 복사하고, 'purge=True' 옵션은 대상 폴더의 불필요한 파일을 삭제합니다.
    sync(source_path, target_path, 'sync', purge=True)
    #print(os.path.exists(target_path))