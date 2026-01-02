"""
Profile 데이터 분석 모듈

배터리 profile 데이터를 분석, 필터링, 시각화하는 함수들을 제공합니다.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional, Tuple


# ============================================================================
# 데이터 구조 분석 함수
# ============================================================================

def analyze_profile_structure(loaded_data: Dict) -> pd.DataFrame:
    """
    Profile 데이터 구조 분석 및 요약
    
    Parameters:
        loaded_data (dict): process_battery_data()에서 반환된 loaded_data
    
    Returns:
        pd.DataFrame: 각 채널별 데이터 요약 정보
    """
    summary_data = []
    
    print("=" * 80)
    print("📊 PROFILE 데이터 구조 분석")
    print("=" * 80)
    
    # PNE Profile 데이터 분석
    if loaded_data.get('pne_profile'):
        print("\n🔧 PNE Profile 데이터:")
        print("-" * 80)
        
        for key, df in loaded_data['pne_profile'].items():
            print(f"\n채널: {key}")
            print(f"  - 행 개수: {len(df):,}")
            print(f"  - 컬럼: {list(df.columns)}")
            
            # 고유값 분석
            if 'Condition' in df.columns:
                conditions = df['Condition'].unique()
                print(f"  - Condition 고유값: {sorted(conditions)}")
                for cond in sorted(conditions):
                    count = len(df[df['Condition'] == cond])
                    print(f"    • Condition {cond}: {count:,}행")
            
            if 'EndState' in df.columns:
                endstates = df['EndState'].unique()
                print(f"  - EndState 고유값: {sorted(endstates)[:10]}...")  # 처음 10개만
            
            if 'step' in df.columns:
                steps = df['step'].unique()
                print(f"  - Step 고유값 개수: {len(steps)}")
                print(f"  - Step 범위: {df['step'].min()} ~ {df['step'].max()}")
            
            # 요약 데이터 저장
            summary_data.append({
                'channel': key,
                'type': 'PNE',
                'rows': len(df),
                'columns': len(df.columns),
                'conditions': len(df['Condition'].unique()) if 'Condition' in df.columns else 0,
                'steps': len(df['step'].unique()) if 'step' in df.columns else 0,
                'voltage_range': f"{df['voltage_v'].min():.2f} ~ {df['voltage_v'].max():.2f}" if 'voltage_v' in df.columns else 'N/A',
                'current_range': f"{df['current_mA'].min():.2f} ~ {df['current_mA'].max():.2f}" if 'current_mA' in df.columns else 'N/A'
            })
    
    # Toyo Profile 데이터 분석
    if loaded_data.get('toyo_profile'):
        print("\n\n🔧 Toyo Profile 데이터:")
        print("-" * 80)
        
        for key, df in loaded_data['toyo_profile'].items():
            print(f"\n채널: {key}")
            print(f"  - 행 개수: {len(df):,}")
            print(f"  - 컬럼: {list(df.columns)}")
            
            # 요약 데이터 저장
            summary_data.append({
                'channel': key,
                'type': 'Toyo',
                'rows': len(df),
                'columns': len(df.columns),
                'conditions': 0,
                'steps': 0,
                'voltage_range': 'N/A',
                'current_range': 'N/A'
            })
    
    print("\n" + "=" * 80)
    
    return pd.DataFrame(summary_data)


# ============================================================================
# 필터링 함수
# ============================================================================

def filter_by_condition(df: pd.DataFrame, condition: int) -> pd.DataFrame:
    """
    Condition으로 필터링
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
        condition (int): 1=충전, 2=방전
    
    Returns:
        pd.DataFrame: 필터링된 데이터
    """
    if 'Condition' not in df.columns:
        print("⚠️  'Condition' 컬럼이 없습니다.")
        return df
    
    filtered = df[df['Condition'] == condition].copy()
    
    condition_name = {1: '충전', 2: '방전'}.get(condition, f'Condition {condition}')
    print(f"✓ {condition_name} 데이터 필터링: {len(filtered):,}행 (전체의 {len(filtered)/len(df)*100:.1f}%)")
    
    return filtered


def filter_by_step(df: pd.DataFrame, steps: List[int]) -> pd.DataFrame:
    """
    특정 step으로 필터링
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
        steps (list): 필터링할 step 리스트
    
    Returns:
        pd.DataFrame: 필터링된 데이터
    """
    if 'step' not in df.columns:
        print("⚠️  'step' 컬럼이 없습니다.")
        return df
    
    filtered = df[df['step'].isin(steps)].copy()
    
    print(f"✓ Step {steps} 데이터 필터링: {len(filtered):,}행 (전체의 {len(filtered)/len(df)*100:.1f}%)")
    
    return filtered


def identify_cccv_phases(df: pd.DataFrame, cv_current_threshold: float = 50.0) -> pd.DataFrame:
    """
    CCCV 충전 구간 식별 (CC: Constant Current, CV: Constant Voltage)
    
    Parameters:
        df (pd.DataFrame): 충전 profile 데이터
        cv_current_threshold (float): CV 구간 판단 전류 임계값 (mA)
    
    Returns:
        pd.DataFrame: 'phase' 컬럼이 추가된 데이터 ('CC' 또는 'CV')
    """
    if 'current_mA' not in df.columns:
        print("⚠️  'current_mA' 컬럼이 없습니다.")
        return df
    
    df_copy = df.copy()
    
    # 전류의 절대값이 임계값보다 작으면 CV, 크면 CC
    df_copy['phase'] = df_copy['current_mA'].abs().apply(
        lambda x: 'CV' if x < cv_current_threshold else 'CC'
    )
    
    cc_count = len(df_copy[df_copy['phase'] == 'CC'])
    cv_count = len(df_copy[df_copy['phase'] == 'CV'])
    
    print(f"✓ CCCV 구간 식별 완료:")
    print(f"  - CC (정전류) 구간: {cc_count:,}행 ({cc_count/len(df_copy)*100:.1f}%)")
    print(f"  - CV (정전압) 구간: {cv_count:,}행 ({cv_count/len(df_copy)*100:.1f}%)")
    
    return df_copy


def identify_rpt_cycles(cycle_df: pd.DataFrame, rpt_pattern: Optional[int] = None) -> List[int]:
    """
    RPT (Reference Performance Test) 사이클 식별
    
    Parameters:
        cycle_df (pd.DataFrame): 사이클 데이터
        rpt_pattern (int): RPT 주기 (예: 50이면 50, 100, 150... 사이클)
    
    Returns:
        list: RPT 사이클 번호 리스트
    """
    if 'Cycle' not in cycle_df.columns:
        print("⚠️  'Cycle' 컬럼이 없습니다.")
        return []
    
    all_cycles = sorted(cycle_df['Cycle'].unique())
    
    if rpt_pattern:
        # 패턴 기반 RPT 식별
        rpt_cycles = [c for c in all_cycles if c % rpt_pattern == 0]
    else:
        # 첫 사이클과 마지막 사이클을 RPT로 간주
        rpt_cycles = [all_cycles[0], all_cycles[-1]]
    
    print(f"✓ RPT 사이클 식별: {len(rpt_cycles)}개")
    print(f"  - 사이클 번호: {rpt_cycles[:10]}{'...' if len(rpt_cycles) > 10 else ''}")
    
    return rpt_cycles


# ============================================================================
# 시각화 함수
# ============================================================================

def visualize_profile_overview(df: pd.DataFrame, title: str = "Profile 데이터 개요"):
    """
    Profile 데이터 전체 개요 시각화
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
        title (str): 그래프 제목
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # 전압 프로파일
    if 'voltage_v' in df.columns and 'time_s' in df.columns:
        axes[0].plot(df['time_s'], df['voltage_v'], linewidth=0.5, alpha=0.7)
        axes[0].set_ylabel('전압 (V)', fontsize=12)
        axes[0].set_title(f'{title} - 전압', fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
    
    # 전류 프로파일
    if 'current_mA' in df.columns and 'time_s' in df.columns:
        axes[1].plot(df['time_s'], df['current_mA'], linewidth=0.5, alpha=0.7, color='orange')
        axes[1].set_ylabel('전류 (mA)', fontsize=12)
        axes[1].set_title(f'{title} - 전류', fontsize=14, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
    
    # 용량 프로파일
    if 'ChgCap_mAh' in df.columns and 'DchgCap_mAh' in df.columns and 'time_s' in df.columns:
        axes[2].plot(df['time_s'], df['ChgCap_mAh'], label='충전 용량', linewidth=0.5, alpha=0.7)
        axes[2].plot(df['time_s'], df['DchgCap_mAh'], label='방전 용량', linewidth=0.5, alpha=0.7)
        axes[2].set_xlabel('시간 (s)', fontsize=12)
        axes[2].set_ylabel('용량 (mAh)', fontsize=12)
        axes[2].set_title(f'{title} - 용량', fontsize=14, fontweight='bold')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def visualize_voltage_profile(df: pd.DataFrame, color_by: str = 'Condition', title: str = "전압 프로파일"):
    """
    전압 프로파일 시각화 (Condition 또는 step으로 색상 구분)
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
        color_by (str): 색상 구분 기준 ('Condition' 또는 'step')
        title (str): 그래프 제목
    """
    if 'voltage_v' not in df.columns or 'time_s' not in df.columns:
        print("⚠️  'voltage_v' 또는 'time_s' 컬럼이 없습니다.")
        return
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    if color_by in df.columns:
        unique_values = sorted(df[color_by].unique())
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_values)))
        
        for idx, value in enumerate(unique_values):
            subset = df[df[color_by] == value]
            label = f'{color_by} {value}'
            if color_by == 'Condition':
                label = {1: '충전', 2: '방전'}.get(value, f'Condition {value}')
            
            ax.plot(subset['time_s'], subset['voltage_v'], 
                   label=label, linewidth=0.8, alpha=0.7, color=colors[idx])
    else:
        ax.plot(df['time_s'], df['voltage_v'], linewidth=0.8, alpha=0.7)
    
    ax.set_xlabel('시간 (s)', fontsize=12)
    ax.set_ylabel('전압 (V)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def visualize_current_profile(df: pd.DataFrame, title: str = "전류 프로파일"):
    """
    전류 프로파일 시각화
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
        title (str): 그래프 제목
    """
    if 'current_mA' not in df.columns or 'time_s' not in df.columns:
        print("⚠️  'current_mA' 또는 'time_s' 컬럼이 없습니다.")
        return
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(df['time_s'], df['current_mA'], linewidth=0.8, alpha=0.7, color='orange')
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    
    ax.set_xlabel('시간 (s)', fontsize=12)
    ax.set_ylabel('전류 (mA)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def visualize_capacity_evolution(cycle_df: pd.DataFrame, title: str = "사이클별 용량 변화"):
    """
    사이클별 용량 변화 시각화
    
    Parameters:
        cycle_df (pd.DataFrame): 사이클 데이터
        title (str): 그래프 제목
    """
    if 'Cycle' not in cycle_df.columns:
        print("⚠️  'Cycle' 컬럼이 없습니다.")
        return
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # 충전 용량
    if 'ChgCap_mAh' in cycle_df.columns:
        ax.plot(cycle_df['Cycle'], cycle_df['ChgCap_mAh'], 
               marker='o', markersize=3, label='충전 용량', linewidth=1.5, alpha=0.7)
    
    # 방전 용량
    if 'DchgCap_mAh' in cycle_df.columns:
        ax.plot(cycle_df['Cycle'], cycle_df['DchgCap_mAh'], 
               marker='s', markersize=3, label='방전 용량', linewidth=1.5, alpha=0.7)
    
    # Toyo 데이터의 경우
    if 'Capacity_mAh' in cycle_df.columns:
        ax.plot(cycle_df['Cycle'], cycle_df['Capacity_mAh'], 
               marker='o', markersize=3, label='용량', linewidth=1.5, alpha=0.7)
    
    ax.set_xlabel('사이클', fontsize=12)
    ax.set_ylabel('용량 (mAh)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def visualize_condition_distribution(df: pd.DataFrame, title: str = "Condition 분포"):
    """
    Condition별 데이터 분포 시각화
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
        title (str): 그래프 제목
    """
    if 'Condition' not in df.columns:
        print("⚠️  'Condition' 컬럼이 없습니다.")
        return
    
    condition_counts = df['Condition'].value_counts().sort_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(condition_counts.index, condition_counts.values, alpha=0.7, edgecolor='black')
    
    # 막대 위에 개수 표시
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{int(height):,}',
               ha='center', va='bottom', fontsize=10)
    
    # X축 레이블 변경
    labels = []
    for cond in condition_counts.index:
        label = {1: '충전', 2: '방전'}.get(cond, f'Condition {cond}')
        labels.append(label)
    
    ax.set_xticks(condition_counts.index)
    ax.set_xticklabels(labels)
    ax.set_xlabel('Condition', fontsize=12)
    ax.set_ylabel('데이터 개수', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.show()


# ============================================================================
# 유틸리티 함수
# ============================================================================

def get_profile_summary(df: pd.DataFrame) -> Dict:
    """
    Profile 데이터 요약 정보 반환
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
    
    Returns:
        dict: 요약 정보
    """
    summary = {
        'total_rows': len(df),
        'columns': list(df.columns),
        'time_range': f"{df['time_s'].min():.2f} ~ {df['time_s'].max():.2f} s" if 'time_s' in df.columns else 'N/A',
        'voltage_range': f"{df['voltage_v'].min():.2f} ~ {df['voltage_v'].max():.2f} V" if 'voltage_v' in df.columns else 'N/A',
        'current_range': f"{df['current_mA'].min():.2f} ~ {df['current_mA'].max():.2f} mA" if 'current_mA' in df.columns else 'N/A',
    }
    
    if 'Condition' in df.columns:
        summary['conditions'] = df['Condition'].unique().tolist()
    
    if 'step' in df.columns:
        summary['steps'] = len(df['step'].unique())
    
    return summary


if __name__ == "__main__":
    print("Profile Analyzer 모듈")
    print("사용 가능한 함수:")
    print("  - analyze_profile_structure()")
    print("  - filter_by_condition()")
    print("  - filter_by_step()")
    print("  - identify_cccv_phases()")
    print("  - identify_rpt_cycles()")
    print("  - visualize_profile_overview()")
    print("  - visualize_voltage_profile()")
    print("  - visualize_current_profile()")
    print("  - visualize_capacity_evolution()")
    print("  - visualize_condition_distribution()")
    print("  - get_profile_summary()")
