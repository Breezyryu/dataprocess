"""
Profile ?°ì´??ë¶„ì„ ëª¨ë“ˆ

ë°°í„°ë¦?profile ?°ì´?°ë? ë¶„ì„, ?„í„°ë§? ?œê°?”í•˜???¨ìˆ˜?¤ì„ ?œê³µ?©ë‹ˆ??
?¸í„°?™í‹°ë¸??œê°?”ë? ?„í•´ Plotlyë¥??¬ìš©?©ë‹ˆ??
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple


# ============================================================================
# ?°ì´??êµ¬ì¡° ë¶„ì„ ?¨ìˆ˜
# ============================================================================

def analyze_profile_structure(loaded_data: Dict) -> pd.DataFrame:
    """
    Profile ?°ì´??êµ¬ì¡° ë¶„ì„ ë°??”ì•½
    
    Parameters:
        loaded_data (dict): process_battery_data()?ì„œ ë°˜í™˜??loaded_data
    
    Returns:
        pd.DataFrame: ê°?ì±„ë„ë³??°ì´???”ì•½ ?•ë³´
    """
    summary_data = []
    
    print("=" * 80)
    print("?“Š PROFILE ?°ì´??êµ¬ì¡° ë¶„ì„")
    print("=" * 80)
    
    # PNE Profile ?°ì´??ë¶„ì„
    if loaded_data.get('pne_profile'):
        print("\n?”§ PNE Profile ?°ì´??")
        print("-" * 80)
        
        for key, df in loaded_data['pne_profile'].items():
            print(f"\nì±„ë„: {key}")
            print(f"  - ??ê°œìˆ˜: {len(df):,}")
            print(f"  - ì»¬ëŸ¼: {list(df.columns)}")
            
            # ê³ ìœ ê°?ë¶„ì„
            if 'Condition' in df.columns:
                conditions = df['Condition'].unique()
                print(f"  - Condition ê³ ìœ ê°? {sorted(conditions)}")
                for cond in sorted(conditions):
                    count = len(df[df['Condition'] == cond])
                    print(f"    ??Condition {cond}: {count:,}??)
            
            if 'EndState' in df.columns:
                endstates = df['EndState'].unique()
                print(f"  - EndState ê³ ìœ ê°? {sorted(endstates)[:10]}...")  # ì²˜ìŒ 10ê°œë§Œ
            
            if 'step' in df.columns:
                steps = df['step'].unique()
                print(f"  - Step ê³ ìœ ê°?ê°œìˆ˜: {len(steps)}")
                print(f"  - Step ë²”ìœ„: {df['step'].min()} ~ {df['step'].max()}")
            
            # ?”ì•½ ?°ì´???€??
            summary_data.append({
                'channel': key,
                'type': 'PNE',
                'rows': len(df),
                'columns': len(df.columns),
                'conditions': len(df['Condition'].unique()) if 'Condition' in df.columns else 0,
                'steps': len(df['step'].unique()) if 'step' in df.columns else 0,
                'voltage_range': f"{df['Voltage_V'].min():.2f} ~ {df['Voltage_V'].max():.2f}" if 'Voltage_V' in df.columns else 'N/A',
                'current_range': f"{df['Current_mA'].min():.2f} ~ {df['Current_mA'].max():.2f}" if 'Current_mA' in df.columns else 'N/A'
            })
    
    # Toyo Profile ?°ì´??ë¶„ì„
    if loaded_data.get('toyo_profile'):
        print("\n\n?”§ Toyo Profile ?°ì´??")
        print("-" * 80)
        
        for key, df in loaded_data['toyo_profile'].items():
            print(f"\nì±„ë„: {key}")
            print(f"  - ??ê°œìˆ˜: {len(df):,}")
            print(f"  - ì»¬ëŸ¼: {list(df.columns)}")
            
            # ?”ì•½ ?°ì´???€??
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
# ?„í„°ë§??¨ìˆ˜
# ============================================================================

def filter_by_condition(df: pd.DataFrame, condition: int) -> pd.DataFrame:
    """
    Condition?¼ë¡œ ?„í„°ë§?
    
    Parameters:
        df (pd.DataFrame): Profile ?°ì´??
        condition (int): 1=ì¶©ì „, 2=ë°©ì „
    
    Returns:
        pd.DataFrame: ?„í„°ë§ëœ ?°ì´??
    """
    if 'Condition' not in df.columns:
        print("? ï¸  'Condition' ì»¬ëŸ¼???†ìŠµ?ˆë‹¤.")
        return df
    
    filtered = df[df['Condition'] == condition].copy()
    
    condition_name = {1: 'ì¶©ì „', 2: 'ë°©ì „'}.get(condition, f'Condition {condition}')
    print(f"??{condition_name} ?°ì´???„í„°ë§? {len(filtered):,}??(?„ì²´??{len(filtered)/len(df)*100:.1f}%)")
    
    return filtered


def filter_by_step(df: pd.DataFrame, steps: List[int]) -> pd.DataFrame:
    """
    ?¹ì • step?¼ë¡œ ?„í„°ë§?
    
    Parameters:
        df (pd.DataFrame): Profile ?°ì´??
        steps (list): ?„í„°ë§í•  step ë¦¬ìŠ¤??
    
    Returns:
        pd.DataFrame: ?„í„°ë§ëœ ?°ì´??
    """
    if 'step' not in df.columns:
        print("? ï¸  'step' ì»¬ëŸ¼???†ìŠµ?ˆë‹¤.")
        return df
    
    filtered = df[df['step'].isin(steps)].copy()
    
    print(f"??Step {steps} ?°ì´???„í„°ë§? {len(filtered):,}??(?„ì²´??{len(filtered)/len(df)*100:.1f}%)")
    
    return filtered


def identify_cccv_phases(df: pd.DataFrame, cv_current_threshold: float = 50.0) -> pd.DataFrame:
    """
    CCCV ì¶©ì „ êµ¬ê°„ ?ë³„ (CC: Constant Current, CV: Constant Voltage)
    
    Parameters:
        df (pd.DataFrame): ì¶©ì „ profile ?°ì´??
        cv_current_threshold (float): CV êµ¬ê°„ ?ë‹¨ ?„ë¥˜ ?„ê³„ê°?(mA)
    
    Returns:
        pd.DataFrame: 'phase' ì»¬ëŸ¼??ì¶”ê????°ì´??('CC' ?ëŠ” 'CV')
    """
    if 'Current_mA' not in df.columns:
        print("? ï¸  'Current_mA' ì»¬ëŸ¼???†ìŠµ?ˆë‹¤.")
        return df
    
    df_copy = df.copy()
    
    # ?„ë¥˜???ˆë?ê°’ì´ ?„ê³„ê°’ë³´???‘ìœ¼ë©?CV, ?¬ë©´ CC
    df_copy['phase'] = df_copy['Current_mA'].abs().apply(
        lambda x: 'CV' if x < cv_current_threshold else 'CC'
    )
    
    cc_count = len(df_copy[df_copy['phase'] == 'CC'])
    cv_count = len(df_copy[df_copy['phase'] == 'CV'])
    
    print(f"??CCCV êµ¬ê°„ ?ë³„ ?„ë£Œ:")
    print(f"  - CC (?•ì „ë¥? êµ¬ê°„: {cc_count:,}??({cc_count/len(df_copy)*100:.1f}%)")
    print(f"  - CV (?•ì „?? êµ¬ê°„: {cv_count:,}??({cv_count/len(df_copy)*100:.1f}%)")
    
    return df_copy


def identify_rpt_cycles(cycle_df: pd.DataFrame, rpt_pattern: Optional[int] = None) -> List[int]:
    """
    RPT (Reference Performance Test) ?¬ì´???ë³„
    
    Parameters:
        cycle_df (pd.DataFrame): ?¬ì´???°ì´??
        rpt_pattern (int): RPT ì£¼ê¸° (?? 50?´ë©´ 50, 100, 150... ?¬ì´??
    
    Returns:
        list: RPT ?¬ì´??ë²ˆí˜¸ ë¦¬ìŠ¤??
    """
    if 'Cycle' not in cycle_df.columns:
        print("? ï¸  'Cycle' ì»¬ëŸ¼???†ìŠµ?ˆë‹¤.")
        return []
    
    all_cycles = sorted(cycle_df['Cycle'].unique())
    
    if rpt_pattern:
        # ?¨í„´ ê¸°ë°˜ RPT ?ë³„
        rpt_cycles = [c for c in all_cycles if c % rpt_pattern == 0]
    else:
        # ì²??¬ì´?´ê³¼ ë§ˆì?ë§??¬ì´?´ì„ RPTë¡?ê°„ì£¼
        rpt_cycles = [all_cycles[0], all_cycles[-1]]
    
    print(f"??RPT ?¬ì´???ë³„: {len(rpt_cycles)}ê°?)
    print(f"  - ?¬ì´??ë²ˆí˜¸: {rpt_cycles[:10]}{'...' if len(rpt_cycles) > 10 else ''}")
    
    return rpt_cycles


# ============================================================================
# ?±ëŠ¥ ìµœì ???¨ìˆ˜
# ============================================================================

def downsample_data(df: pd.DataFrame, max_points: int = 10000) -> pd.DataFrame:
    """
    ?€?©ëŸ‰ ?°ì´???¤ìš´?˜í”Œë§?(?œê°???±ëŠ¥ ìµœì ??
    
    Parameters:
        df (pd.DataFrame): ?ë³¸ ?°ì´??
        max_points (int): ìµœë? ?°ì´???¬ì¸????
    
    Returns:
        pd.DataFrame: ?¤ìš´?˜í”Œë§ëœ ?°ì´??
    """
    if len(df) <= max_points:
        return df
    
    # ê· ë“± ê°„ê²© ?˜í”Œë§?
    step = len(df) // max_points
    sampled = df.iloc[::step].copy()
    
    print(f"?“‰ ?¤ìš´?˜í”Œë§? {len(df):,}????{len(sampled):,}??(?œê°???±ëŠ¥ ìµœì ??")
    
    return sampled


# ============================================================================
# ?œê°???¨ìˆ˜ (Plotly ?¸í„°?™í‹°ë¸?
# ============================================================================

def visualize_profile_overview(df: pd.DataFrame, title: str = "Profile ?°ì´??ê°œìš”", 
                               max_points: int = 50000):
    """
    Profile ?°ì´???„ì²´ ê°œìš” ?œê°??(?¸í„°?™í‹°ë¸?
    
    Parameters:
        df (pd.DataFrame): Profile ?°ì´??
        title (str): ê·¸ë˜???œëª©
        max_points (int): ìµœë? ?œì‹œ ?¬ì¸????(?±ëŠ¥ ìµœì ??
    """
    # ?¤ìš´?˜í”Œë§?
    df_plot = downsample_data(df, max_points)
    
    # ?œë¸Œ?Œë¡¯ ?ì„±
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('?„ì•• (V)', '?„ë¥˜ (mA)', '?©ëŸ‰ (mAh)'),
        vertical_spacing=0.08,
        shared_xaxes=True
    )
    
    # ?„ì•• ?„ë¡œ?Œì¼
    if 'Voltage_V' in df_plot.columns and 'time_s' in df_plot.columns:
        fig.add_trace(
            go.Scatter(
                x=df_plot['time_s'], 
                y=df_plot['Voltage_V'],
                mode='lines',
                name='?„ì••',
                line=dict(color='#1f77b4', width=1),
                hovertemplate='?œê°„: %{x:.0f}s<br>?„ì••: %{y:.2f}V<extra></extra>'
            ),
            row=1, col=1
        )
    
    # ?„ë¥˜ ?„ë¡œ?Œì¼
    if 'Current_mA' in df_plot.columns and 'time_s' in df_plot.columns:
        fig.add_trace(
            go.Scatter(
                x=df_plot['time_s'], 
                y=df_plot['Current_mA'],
                mode='lines',
                name='?„ë¥˜',
                line=dict(color='#ff7f0e', width=1),
                hovertemplate='?œê°„: %{x:.0f}s<br>?„ë¥˜: %{y:.2f}mA<extra></extra>'
            ),
            row=2, col=1
        )
    
    # ?©ëŸ‰ ?„ë¡œ?Œì¼
    if 'ChgCap_mAh' in df_plot.columns and 'DchgCap_mAh' in df_plot.columns and 'time_s' in df_plot.columns:
        fig.add_trace(
            go.Scatter(
                x=df_plot['time_s'], 
                y=df_plot['ChgCap_mAh'],
                mode='lines',
                name='ì¶©ì „ ?©ëŸ‰',
                line=dict(color='#2ca02c', width=1),
                hovertemplate='?œê°„: %{x:.0f}s<br>ì¶©ì „: %{y:.2f}mAh<extra></extra>'
            ),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df_plot['time_s'], 
                y=df_plot['DchgCap_mAh'],
                mode='lines',
                name='ë°©ì „ ?©ëŸ‰',
                line=dict(color='#d62728', width=1),
                hovertemplate='?œê°„: %{x:.0f}s<br>ë°©ì „: %{y:.2f}mAh<extra></extra>'
            ),
            row=3, col=1
        )
    
    # ?ˆì´?„ì›ƒ ?¤ì •
    fig.update_xaxes(title_text="?œê°„ (s)", row=3, col=1)
    fig.update_yaxes(title_text="?„ì•• (V)", row=1, col=1)
    fig.update_yaxes(title_text="?„ë¥˜ (mA)", row=2, col=1)
    fig.update_yaxes(title_text="?©ëŸ‰ (mAh)", row=3, col=1)
    
    fig.update_layout(
        title=title,
        height=900,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )
    
    fig.show()


def visualize_voltage_profile(df: pd.DataFrame, color_by: str = 'Condition', 
                              title: str = "?„ì•• ?„ë¡œ?Œì¼", max_points: int = 50000):
    """
    ?„ì•• ?„ë¡œ?Œì¼ ?œê°??(Condition ?ëŠ” step?¼ë¡œ ?‰ìƒ êµ¬ë¶„, ?¸í„°?™í‹°ë¸?
    
    Parameters:
        df (pd.DataFrame): Profile ?°ì´??
        color_by (str): ?‰ìƒ êµ¬ë¶„ ê¸°ì? ('Condition' ?ëŠ” 'step')
        title (str): ê·¸ë˜???œëª©
        max_points (int): ìµœë? ?œì‹œ ?¬ì¸????
    """
    if 'Voltage_V' not in df.columns or 'time_s' not in df.columns:
        print("? ï¸  'Voltage_V' ?ëŠ” 'time_s' ì»¬ëŸ¼???†ìŠµ?ˆë‹¤.")
        return
    
    # ?¤ìš´?˜í”Œë§?
    df_plot = downsample_data(df, max_points)
    
    fig = go.Figure()
    
    if color_by in df_plot.columns:
        unique_values = sorted(df_plot[color_by].unique())
        colors = px.colors.qualitative.Plotly
        
        for idx, value in enumerate(unique_values):
            subset = df_plot[df_plot[color_by] == value]
            label = f'{color_by} {value}'
            if color_by == 'Condition':
                label = {1: 'ì¶©ì „', 2: 'ë°©ì „', 3: 'Rest', 8: 'CCCV'}.get(value, f'Condition {value}')
            
            fig.add_trace(
                go.Scatter(
                    x=subset['time_s'],
                    y=subset['Voltage_V'],
                    mode='lines',
                    name=label,
                    line=dict(color=colors[idx % len(colors)], width=1.5),
                    hovertemplate=f'{label}<br>?œê°„: %{{x:.0f}}s<br>?„ì••: %{{y:.2f}}V<extra></extra>'
                )
            )
    else:
        fig.add_trace(
            go.Scatter(
                x=df_plot['time_s'],
                y=df_plot['Voltage_V'],
                mode='lines',
                name='?„ì••',
                line=dict(width=1.5),
                hovertemplate='?œê°„: %{x:.0f}s<br>?„ì••: %{y:.2f}V<extra></extra>'
            )
        )
    
    fig.update_layout(
        title=title,
        xaxis_title='?œê°„ (s)',
        yaxis_title='?„ì•• (V)',
        height=600,
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    fig.show()


def visualize_current_profile(df: pd.DataFrame, title: str = "?„ë¥˜ ?„ë¡œ?Œì¼", 
                              max_points: int = 50000):
    """
    ?„ë¥˜ ?„ë¡œ?Œì¼ ?œê°??(?¸í„°?™í‹°ë¸?
    
    Parameters:
        df (pd.DataFrame): Profile ?°ì´??
        title (str): ê·¸ë˜???œëª©
        max_points (int): ìµœë? ?œì‹œ ?¬ì¸????
    """
    if 'Current_mA' not in df.columns or 'time_s' not in df.columns:
        print("? ï¸  'Current_mA' ?ëŠ” 'time_s' ì»¬ëŸ¼???†ìŠµ?ˆë‹¤.")
        return
    
    # ?¤ìš´?˜í”Œë§?
    df_plot = downsample_data(df, max_points)
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df_plot['time_s'],
            y=df_plot['Current_mA'],
            mode='lines',
            name='?„ë¥˜',
            line=dict(color='#ff7f0e', width=1.5),
            hovertemplate='?œê°„: %{x:.0f}s<br>?„ë¥˜: %{y:.2f}mA<extra></extra>'
        )
    )
    
    # 0 ê¸°ì???
    fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
    
    fig.update_layout(
        title=title,
        xaxis_title='?œê°„ (s)',
        yaxis_title='?„ë¥˜ (mA)',
        height=600,
        hovermode='x unified',
        template='plotly_white'
    )
    
    fig.show()


def visualize_capacity_evolution(cycle_df: pd.DataFrame, title: str = "?¬ì´?´ë³„ ?©ëŸ‰ ë³€??):
    """
    ?¬ì´?´ë³„ ?©ëŸ‰ ë³€???œê°??(?¸í„°?™í‹°ë¸?
    
    Parameters:
        cycle_df (pd.DataFrame): ?¬ì´???°ì´??
        title (str): ê·¸ë˜???œëª©
    """
    if 'Cycle' not in cycle_df.columns:
        print("? ï¸  'Cycle' ì»¬ëŸ¼???†ìŠµ?ˆë‹¤.")
        return
    
    fig = go.Figure()
    
    # ì¶©ì „ ?©ëŸ‰
    if 'ChgCap_mAh' in cycle_df.columns:
        fig.add_trace(
            go.Scatter(
                x=cycle_df['Cycle'],
                y=cycle_df['ChgCap_mAh'],
                mode='lines+markers',
                name='ì¶©ì „ ?©ëŸ‰',
                marker=dict(size=4),
                line=dict(width=2),
                hovertemplate='?¬ì´?? %{x}<br>ì¶©ì „: %{y:.2f}mAh<extra></extra>'
            )
        )
    
    # ë°©ì „ ?©ëŸ‰
    if 'DchgCap_mAh' in cycle_df.columns:
        fig.add_trace(
            go.Scatter(
                x=cycle_df['Cycle'],
                y=cycle_df['DchgCap_mAh'],
                mode='lines+markers',
                name='ë°©ì „ ?©ëŸ‰',
                marker=dict(size=4, symbol='square'),
                line=dict(width=2),
                hovertemplate='?¬ì´?? %{x}<br>ë°©ì „: %{y:.2f}mAh<extra></extra>'
            )
        )
    
    # Toyo ?°ì´?°ì˜ ê²½ìš°
    if 'Capacity_mAh' in cycle_df.columns:
        fig.add_trace(
            go.Scatter(
                x=cycle_df['Cycle'],
                y=cycle_df['Capacity_mAh'],
                mode='lines+markers',
                name='?©ëŸ‰',
                marker=dict(size=4),
                line=dict(width=2),
                hovertemplate='?¬ì´?? %{x}<br>?©ëŸ‰: %{y:.2f}mAh<extra></extra>'
            )
        )
    
    fig.update_layout(
        title=title,
        xaxis_title='?¬ì´??,
        yaxis_title='?©ëŸ‰ (mAh)',
        height=600,
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.show()


def visualize_condition_distribution(df: pd.DataFrame, title: str = "Condition ë¶„í¬"):
    """
    Conditionë³??°ì´??ë¶„í¬ ?œê°??(?¸í„°?™í‹°ë¸?
    
    Parameters:
        df (pd.DataFrame): Profile ?°ì´??
        title (str): ê·¸ë˜???œëª©
    """
    if 'Condition' not in df.columns:
        print("? ï¸  'Condition' ì»¬ëŸ¼???†ìŠµ?ˆë‹¤.")
        return
    
    condition_counts = df['Condition'].value_counts().sort_index()
    
    # ?ˆì´ë¸?ë³€ê²?
    labels = []
    for cond in condition_counts.index:
        label = {1: 'ì¶©ì „', 2: 'ë°©ì „', 3: 'Rest', 8: 'CCCV'}.get(cond, f'Condition {cond}')
        labels.append(label)
    
    # ë¹„ìœ¨ ê³„ì‚°
    total = condition_counts.sum()
    percentages = (condition_counts / total * 100).round(1)
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            x=labels,
            y=condition_counts.values,
            text=[f'{count:,}<br>({pct}%)' for count, pct in zip(condition_counts.values, percentages)],
            textposition='outside',
            marker=dict(
                color=condition_counts.values,
                colorscale='Viridis',
                showscale=False
            ),
            hovertemplate='%{x}<br>ê°œìˆ˜: %{y:,}<br>ë¹„ìœ¨: %{text}<extra></extra>'
        )
    )
    
    fig.update_layout(
        title=title,
        xaxis_title='Condition',
        yaxis_title='?°ì´??ê°œìˆ˜',
        height=600,
        template='plotly_white',
        showlegend=False
    )
    
    fig.show()


# ============================================================================
# ? í‹¸ë¦¬í‹° ?¨ìˆ˜
# ============================================================================

def get_profile_summary(df: pd.DataFrame) -> Dict:
    """
    Profile ?°ì´???”ì•½ ?•ë³´ ë°˜í™˜
    
    Parameters:
        df (pd.DataFrame): Profile ?°ì´??
    
    Returns:
        dict: ?”ì•½ ?•ë³´
    """
    summary = {
        'total_rows': len(df),
        'columns': list(df.columns),
        'time_range': f"{df['time_s'].min():.2f} ~ {df['time_s'].max():.2f} s" if 'time_s' in df.columns else 'N/A',
        'voltage_range': f"{df['Voltage_V'].min():.2f} ~ {df['Voltage_V'].max():.2f} V" if 'Voltage_V' in df.columns else 'N/A',
        'current_range': f"{df['Current_mA'].min():.2f} ~ {df['Current_mA'].max():.2f} mA" if 'Current_mA' in df.columns else 'N/A',
    }
    
    if 'Condition' in df.columns:
        summary['conditions'] = df['Condition'].unique().tolist()
    
    if 'step' in df.columns:
        summary['steps'] = len(df['step'].unique())
    
    return summary


if __name__ == "__main__":
    print("Profile Analyzer ëª¨ë“ˆ (Plotly ?¸í„°?™í‹°ë¸?ë²„ì „)")
    print("?¬ìš© ê°€?¥í•œ ?¨ìˆ˜:")
    print("  - analyze_profile_structure()")
    print("  - filter_by_condition()")
    print("  - filter_by_step()")
    print("  - identify_cccv_phases()")
    print("  - identify_rpt_cycles()")
    print("  - downsample_data()")
    print("  - visualize_profile_overview()")
    print("  - visualize_voltage_profile()")
    print("  - visualize_current_profile()")
    print("  - visualize_capacity_evolution()")
    print("  - visualize_condition_distribution()")
    print("  - get_profile_summary()")
