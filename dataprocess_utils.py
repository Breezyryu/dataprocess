import os
import re
import pandas as pd

def check_cycler(raw_file_path):
    """
    충방전기 구분 (패턴 폴더 유무로 구분)
    
    Parameters:
        raw_file_path (str): 분석할 데이터 경로
    
    Returns:
        str: 'PNE' 또는 'Toyo'
    """
    has_pattern = os.path.isdir(os.path.join(raw_file_path, "Pattern"))
    return "PNE" if has_pattern else "Toyo"


def name_capacity(data_file_path):
    """
    filepath 이름에서 용량을 추출하는 함수
    
    Parameters:
        data_file_path (str): 데이터 경로
    
    Returns:
        float or None: 추출된 용량 (mAh), 없으면 None
    """
    raw_file_path = re.sub(r'[._@$()]', ' ', data_file_path)
    match = re.search(r'(\d+([\-.] \d+)?)mAh', raw_file_path)
    if match:
        min_cap = match.group(1).replace('-', '.')
        return float(min_cap)
    return None


def get_directory_info(path):
    """
    디렉토리 메타 정보 추출
    
    Parameters:
        path (str): 분석할 디렉토리 경로
    
    Returns:
        dict: 폴더명, 서브폴더 개수, 파일 개수, Pattern 폴더 유무, 경로 존재 여부
    """
    info = {
        'path': path,
        'folder_name': os.path.basename(path),
        'exists': os.path.exists(path),
        'has_pattern': False,
        'num_subfolders': 0,
        'num_files': 0,
        'cycler_type': 'Unknown',
        'capacity_mAh': None
    }
    
    if info['exists']:
        info['has_pattern'] = os.path.isdir(os.path.join(path, "Pattern"))
        info['cycler_type'] = check_cycler(path)
        
        try:
            items = os.listdir(path)
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    info['num_subfolders'] += 1
                else:
                    info['num_files'] += 1
        except PermissionError:
            pass
        
        info['capacity_mAh'] = name_capacity(path)
    
    return info

def find_pne_channel_folders(path):
    """
    PNE 채널 폴더 찾기 (M**Ch***[***] 패턴)
    
    Parameters:
        path (str): PNE 데이터 경로
    
    Returns:
        list: 채널 폴더 경로 리스트
    """
    if not os.path.exists(path):
        return []
    
    channel_folders = []
    pattern = re.compile(r'M\d{2}Ch\d{3}\[\d{3}\]')
    
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path) and pattern.match(item):
            channel_folders.append(item_path)
    
    channel_folders.sort()
    return channel_folders


def find_toyo_channel_folders(path):
    """
    Toyo 채널 폴더 찾기 (숫자로만 이루어진 폴더)
    
    Parameters:
        path (str): Toyo 데이터 경로
    
    Returns:
        list: 채널 폴더 경로 리스트
    """
    if not os.path.exists(path):
        return []
    
    channel_folders = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path) and item.isdigit():
            channel_folders.append(item_path)
    
    channel_folders.sort()
    return channel_folders

def load_pne_cycle_data(channel_path):
    """
    PNE 사이클 데이터 로딩 (SaveEndData.csv)
    """
    restore_path = os.path.join(channel_path, "Restore")
    
    if not os.path.isdir(restore_path):
        return None
    
    csv_files = [f for f in os.listdir(restore_path) if f.endswith('.csv')]
    end_data_file = None
    
    for file in csv_files:
        if 'SaveEndData' in file:
            end_data_file = file
            break
    
    if not end_data_file:
        return None
    
    try:
        file_path = os.path.join(restore_path, end_data_file)
        if os.stat(file_path).st_size == 0:
            return None
        
        df = pd.read_csv(file_path, sep=',', skiprows=0, engine='c', 
                        header=None, encoding='cp949', on_bad_lines='skip')
        
        df = df[[27, 2, 10, 11, 8, 20, 45, 14, 15, 17, 24, 6, 9]]
        df.columns = ['Cycle', 'Condition', 'ChgCap_mAh','DchgCap_mAh',
        'OCV_mV','imp', 'VoltageMax_mV','ChgPow_mW','DchgPow_mW',
        'Steptime_s', 'Temp_C', 'EndState', 'Current_mA']

               
        df['Temp_C'] = df['Temp_C'] / 1000
        df['OCV_mV'] = df['OCV_mV'] / 1000
        df['Current_mA'] = df['Current_mA'] / 1000
        df['DchgCap_mAh'] = df['DchgCap_mAh'] / 1000
        df['ChgCap_mAh'] = df['ChgCap_mAh'] / 1000
        df['VoltageMax_mV'] = df['VoltageMax_mV'] / 1000
        df['Steptime_s'] = df['Steptime_s'] / 100
        
        return df
        
    except Exception as e:
        print(f"  ❌ PNE 사이클 데이터 로딩 실패: {e}")
        return None


def load_pne_profile_data(channel_path):
    """
    PNE 프로파일 데이터 로딩 (SaveData*.csv)
    """
    restore_path = os.path.join(channel_path, "Restore")
    
    if not os.path.isdir(restore_path):
        return None
    
    csv_files = [f for f in os.listdir(restore_path) 
                 if f.endswith('.csv') and 'SaveData' in f and 'SaveEndData' not in f]
    csv_files.sort()
    
    if not csv_files:
        return None
    
    dataframes = []
    for file in csv_files:
        try:
            file_path = os.path.join(restore_path, file)
            df_temp = pd.read_csv(file_path, sep=',', skiprows=0, engine='c',
                                 header=None, encoding='cp949', on_bad_lines='skip')
            dataframes.append(df_temp)
        except:
            continue
    
    if dataframes:
        df_combined = pd.concat(dataframes, ignore_index=True)
        df_combined = df_combined[[0, 18, 19, 8, 9, 21, 10, 11, 7, 17]]
        df_combined.columns = ['index', 'time_day', 'time_s', 'voltage_v', 'current_mA', 
                               'temp_C', 'ChgCap_mAh', 'DchgCap_mAh', 'step', 'steptime_s']
        return df_combined
    else:
        return None

def load_toyo_cycle_data(channel_path):
    """
    Toyo 사이클 데이터 로딩 (capacity.log)
    """
    capacity_file = os.path.join(channel_path, 'capacity.log')
    
    if not os.path.isfile(capacity_file):
        return None
    
    try:
        df = pd.read_csv(capacity_file, sep=',', skiprows=0, engine='c', 
                        encoding='cp949', on_bad_lines='skip')
        
        if 'Cap[mAh]' in df.columns:
            df = df[['TotlCycle', 'Condition', 'Cap[mAh]', 'Ocv', 'PeakTemp[Deg]', 'AveVolt[V]']]
            df.columns = ['Cycle', 'Condition', 'Capacity_mAh', 'OCV_V', 'Temp_C', 'AvgVolt_V']
        elif 'Capacity[mAh]' in df.columns:
            df = df[['Total Cycle', 'Condition', 'Capacity[mAh]', 'OCV[V]', 'Peak Temp.[deg]', 'Ave. Volt.[V]']]
            df.columns = ['Cycle', 'Condition', 'Capacity_mAh', 'OCV_V', 'Temp_C', 'AvgVolt_V']
        
        return df
        
    except Exception as e:
        print(f"  ❌ Toyo 사이클 데이터 로딩 실패: {e}")
        return None



def load_toyo_profile_data(channel_path, max_cycles=3):
    """
    Toyo 프로파일 데이터 로딩 (처음 max_cycles개 사이클만)
    """
    profile_files = []
    
    # 채널 폴더 내의 모든 .csv 파일 찾기
    if not os.path.isdir(channel_path):
        return None
    
    for file in os.listdir(channel_path):
        if file.endswith('.csv') and 'cycle' in file.lower():
            profile_files.append(file)
    
    profile_files.sort()
    
    if not profile_files:
        return None
    
    # 처음 max_cycles개 파일만 로딩
    dataframes = []
    for file in profile_files[:max_cycles]:
        try:
            file_path = os.path.join(channel_path, file)
            df_temp = pd.read_csv(file_path, sep=',', skiprows=0, engine='c',
                                 encoding='cp949', on_bad_lines='skip')
            dataframes.append(df_temp)
        except:
            continue
    
    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    else:
        return None


