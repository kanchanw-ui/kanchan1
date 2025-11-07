import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def create_visualizations(results):
    """Create interactive visualizations for the comparison results"""
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Issues Summary', 'Severity Distribution', 'Issue Types', 'Mismatch Details'),
        specs=[[{"type": "bar"}, {"type": "pie"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # 1. Issues Summary Bar Chart
    summary = results['summary']
    categories = ['Mismatches', 'Duplicates', 'Anomalies']
    values = [
        summary['total_mismatches'],
        summary['total_duplicates'],
        summary['total_anomalies']
    ]
    
    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            name='Issues',
            marker_color=['#FF6B6B', '#4ECDC4', '#FFE66D'],
            text=values,
            textposition='auto'
        ),
        row=1, col=1
    )
    
    # 2. Severity Distribution Pie Chart
    severity_counts = {'High': 0, 'Medium': 0, 'Low': 0}
    for category in ['mismatches', 'duplicates', 'anomalies']:
        for item in results.get(category, []):
            severity = item.get('severity', 'Low')
            if severity in severity_counts:
                severity_counts[severity] += 1
    
    if sum(severity_counts.values()) > 0:
        fig.add_trace(
            go.Pie(
                labels=list(severity_counts.keys()),
                values=list(severity_counts.values()),
                name='Severity',
                marker_colors=['#FF6B6B', '#FFE66D', '#95E1D3']
            ),
            row=1, col=2
        )
    
    # 3. Issue Types Breakdown
    type_counts = {}
    for category in ['mismatches', 'duplicates', 'anomalies']:
        for item in results.get(category, []):
            issue_type = item.get('type', 'Unknown')
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
    
    if type_counts:
        fig.add_trace(
            go.Bar(
                x=list(type_counts.keys()),
                y=list(type_counts.values()),
                name='Issue Types',
                marker_color='#4ECDC4',
                text=list(type_counts.values()),
                textposition='auto'
            ),
            row=2, col=1
        )
    
    # 4. Mismatch Details (if any)
    if results['mismatches']:
        mismatch_items = [item.get('item', 'Unknown') for item in results['mismatches']]
        mismatch_diffs = []
        for item in results['mismatches']:
            try:
                diff = float(item.get('difference', 0))
                mismatch_diffs.append(diff)
            except (ValueError, TypeError):
                mismatch_diffs.append(0)
        
        if mismatch_items:
            fig.add_trace(
                go.Bar(
                    x=mismatch_items[:10],  # Limit to 10 items for readability
                    y=mismatch_diffs[:10],
                    name='Difference Amount',
                    marker_color='#FF6B6B',
                    text=[f"${d:.2f}" for d in mismatch_diffs[:10]],
                    textposition='auto'
                ),
                row=2, col=2
            )
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text="Invoice QA Analysis Dashboard",
        title_x=0.5,
        title_font_size=20
    )
    
    # Update axes labels
    fig.update_xaxes(title_text="Category", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=1)
    fig.update_xaxes(title_text="Issue Type", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    fig.update_xaxes(title_text="Item", row=2, col=2)
    fig.update_yaxes(title_text="Difference ($)", row=2, col=2)
    
    return fig

