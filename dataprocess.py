import os
import pandas as pd
from dataprocess_utils import (
    get_directory_info,
    find_pne_channel_folders,
    find_toyo_channel_folders,
    load_pne_cycle_data,
    load_pne_profile_data,
    load_toyo_cycle_data,
    load_toyo_profile_data
)

def process_battery_data(paths):
    """
    주어진 경로 리스트를 순회하며 배터리 데이터를 처리하고 로드합니다.
    
    Parameters:
        paths (list): 분석할 데이터 디렉토리 경로 리스트
        
    Returns:
        tuple: (df_results (pd.DataFrame), loaded_data (dict))
    """
    # 1. 디렉토리 정보 수집
    results = []
    print(f"분석 대상 경로 개수: {len(paths)}")
    for i, path in enumerate(paths, 1):
        print(f"  {i}. {path}")
        print(f"분석 중: {path}")
        info = get_directory_info(path)
        results.append(info)
        
    df_results = pd.DataFrame(results)
    print(f"\n✅ 총 {len(df_results)}개 경로 분석 완료")
    
    if not df_results.empty:
        print("\n=== 사이클러 타입별 통계 ===")
        print(df_results['cycler_type'].value_counts())

    # 2. 데이터 로딩
    loaded_data = {
        'pne_cycle': {},
        'pne_profile': {},
        'toyo_cycle': {},
        'toyo_profile': {}
    }
    
    for idx, row in df_results.iterrows():
        path = row['path']
        folder_name = row['folder_name']
        cycler_type = row['cycler_type']
        
        print(f"\n{'='*70}")
        print(f"📁 경로: {folder_name}")
        print(f"🔧 타입: {cycler_type}")
        print(f"{'='*70}")
        
        if cycler_type == 'PNE':
            # PNE 채널 폴더 찾기
            channel_folders = find_pne_channel_folders(path)
            
            if channel_folders:
                print(f"  📂 발견된 PNE 채널: {len(channel_folders)}개")
                
                # 모든 채널 처리
                for channel_path in channel_folders:
                    channel_name = os.path.basename(channel_path)
                    print(f"\n  🔄 채널 {channel_name} 로딩 중...")
                    
                    # 사이클 데이터 로딩
                    cycle_df = load_pne_cycle_data(channel_path)
                    if cycle_df is not None:
                        key = f"{folder_name}_{channel_name}"
                        loaded_data['pne_cycle'][key] = cycle_df
                        print(f"    ✅ 사이클 데이터: {len(cycle_df)} rows")
                    
                    # 프로파일 데이터 로딩 (처음 5개 파일만)
                    profile_df = load_pne_profile_data(channel_path)
                    if profile_df is not None:
                        key = f"{folder_name}_{channel_name}"
                        loaded_data['pne_profile'][key] = profile_df
                        print(f"    ✅ 프로파일 데이터: {len(profile_df)} rows")
            else:
                print(f"  ⚠️  PNE 채널 폴더를 찾을 수 없습니다")
        
        elif cycler_type == 'Toyo':
            # Toyo 채널 폴더 찾기
            channel_folders = find_toyo_channel_folders(path)
            
            if channel_folders:
                print(f"  📂 발견된 Toyo 채널: {len(channel_folders)}개")
                
                # 모든 채널 처리
                for channel_path in channel_folders:
                    channel_name = os.path.basename(channel_path)
                    print(f"\n  🔄 채널 {channel_name} 로딩 중...")
                    
                    # 사이클 데이터 로딩
                    cycle_df = load_toyo_cycle_data(channel_path)
                    if cycle_df is not None:
                        key = f"{folder_name}_ch{channel_name}"
                        loaded_data['toyo_cycle'][key] = cycle_df
                        print(f"    ✅ 사이클 데이터: {len(cycle_df)} rows")
                    
                    # 프로파일 데이터 로딩 (처음 3개 사이클만)
                    profile_df = load_toyo_profile_data(channel_path)
                    if profile_df is not None:
                        key = f"{folder_name}_ch{channel_name}"
                        loaded_data['toyo_profile'][key] = profile_df
                        print(f"    ✅ 프로파일 데이터: {len(profile_df)} rows")
            else:
                print(f"  ⚠️  Toyo 채널 폴더를 찾을 수 없습니다")
                
    # 로딩 요약 출력
    print(f"\n\n{'='*70}")
    print("📊 데이터 로딩 요약")
    print(f"{'='*70}")
    print(f"  PNE 사이클 데이터: {len(loaded_data['pne_cycle'])}개 채널")
    print(f"  PNE 프로파일 데이터: {len(loaded_data['pne_profile'])}개 채널")
    print(f"  Toyo 사이클 데이터: {len(loaded_data['toyo_cycle'])}개 채널")
    print(f"  Toyo 프로파일 데이터: {len(loaded_data['toyo_profile'])}개 채널")
    
    return df_results, loaded_data

def main():
    # 기본 분석 경로 설정 (테스트용)
    default_paths = [
        r"C:\Users\Ryu\Python_project\data\dataprocess\Rawdata\A1_MP1_4500mAh_T23_1",
        # 추가 테스트 경로...
    ]
    
    process_battery_data(default_paths)

if __name__ == "__main__":
    main()
