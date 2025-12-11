# ChartMaster Pro - Quick Start Guide

## Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run Application**
```bash
streamlit run app.py
```

3. **Access Pages**
- Dashboard: http://localhost:8501
- Scanner: http://localhost:8501/scanner
- Charts: http://localhost:8501/charts
- Calendar: http://localhost:8501/calendar
- Backtest: http://localhost:8501/backtest
- Watchlists: http://localhost:8501/watchlists
- Research: http://localhost:8501/research

## Key Features Implemented

✅ Complete Design System dengan CSS Variables
✅ Professional Header & Navigation
✅ Dashboard Grid Layout
✅ Market Scanner dengan Advanced Filters
✅ Advanced Charts dengan Multiple Layouts
✅ Economic Calendar dengan Event Details
✅ Backtesting Interface
✅ Watchlist Manager
✅ Research Tools (Sector, Seasonality, Intermarket)

## Customization

### Changing Colors
Edit `static/css/design-system.css` dan update CSS variables:
```css
:root {
    --color-accent-blue: #4361EE; /* Change primary color */
    --color-bullish-green: #06D6A0; /* Change positive color */
    /* ... */
}
```

### Adding New Widgets
Use `render_widget()` function:
```python
from components.ui_components import render_widget

widget = render_widget(
    title="My Widget",
    content="<p>Content here</p>",
    size="medium"
)
st.markdown(widget, unsafe_allow_html=True)
```

### Creating New Pages
1. Create file in `pages/` directory
2. Import design system: `load_design_system()`
3. Render header: `render_header(nav_items, "Page Name")`
4. Add page to navigation items

## Notes

- Design system menggunakan CSS Variables untuk easy theming
- Semua komponen responsive untuk mobile/tablet/desktop
- Dark theme adalah default, light theme dapat ditambahkan
- Icons menggunakan SVG inline untuk performance
- Animations menggunakan CSS transitions untuk smooth UX

