# AdventureWorks Sales Analytics Dashboard 🚴‍♂️

Welcome to the **AdventureWorks Sales Analytics Dashboard**, an interactive Business Intelligence solution built entirely in Python using **Streamlit** and **Plotly**. This project analyzes over 60,000 historical sales transactions (2005-2008) across 6 countries for a fictional bicycle manufacturing company.

## 🌟 Key Features
- **Comprehensive Executive Overview:** Instantly track $969M+ in total revenue, profits, COGS, and customer growth.
- **Dynamic KPI Cards:** Custom HTML/CSS styled KPI cards providing top-level metrics at a glance.
- **Interactive Multi-Level Filtering:** Slice and dice the data globally by:
  - Year
  - Country/Region
  - Product Category
  - Supervisor
  - Customer Gender
- **Deep-Dive Analytics Modules:**
  - 📈 **Sales Performance:** Track top-performing salespeople, supervisors, and sales channels.
  - 🛒 **Product & Category:** Analyze cost vs. profit margins using scatter plots, and review top-selling product colors per sales reason.
  - 👥 **Customer Demographics:** Understand revenue distribution by gender, education level, age group, and identify the top 10 most profitable customers.
  - 🌍 **Geographic Analysis:** Explore regional performance and shipping times.
  - 🔍 **Detailed Data Explorer:** A tabular view of raw data with CSV export functionality.

## 🛠️ Technology Stack
- **Python 3** (Core Language)
- **Streamlit** (Web Application Framework & UI)
- **Pandas** (Data Manipulation & Cleaning)
- **Plotly Express / Graph Objects** (Interactive Visualizations)
- **Custom CSS** (Premium Dark Navy UI/UX Theme)

## 📂 Repository Structure
- `streamlit_app.py`: The main entry point of the dashboard. Handles navigation, global filters, and state.
- `components/`: Contains modular pages for the dashboard:
  - `executive_overview.py`
  - `sales_performance.py`
  - `product_analysis.py`
  - `customer_analysis.py`
  - `geographic_analysis.py`
  - `detailed_data.py`
- `utils/`: Reusable helper functions and constants.
  - `data_loader.py`: Handles loading and formatting of the dataset (CSV/Excel fallback).
  - `theme.py`: Defines the global color palette and Plotly chart layouts.
- `Enriched_Sales_Data.csv`: The optimized flat-file dataset used by the dashboard.
- `Cleaned_Data_Model.xlsx`: The Star Schema Data Model built from the raw data.
- `Regional_Sales_Pivot_Charts_Dashboard.xlsx`: An Excel-based dashboard counterpart.
- `Senior_Data_Analyst_Report.md`: A detailed analytical report answering specific business questions and providing strategic insights.

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd "DATA ANALYSIS"
   ```

2. **Install dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install streamlit pandas plotly openpyxl
   ```

3. **Launch the Dashboard:**
   ```bash
   python -m streamlit run streamlit_app.py
   ```
   *Note: The app will automatically open in your default browser at `http://localhost:8501`.*

## 📊 Analytics Highlights
- **Highest Profitable Quarter:** Q1 of 2008 represents over 51% of total historical sales, indicating a massive spike in Q1.
- **Top Product Category:** `Accessories` drive the highest volume (866k units) and represent 63.5% of total revenue.
- **Strategic Recommendation:** Consider discontinuing low-performing models such as `Mountain-100` and `Road-650` due to high production costs and poor net profit generation.

---
*Built with ❤️ for advanced Data Analysis & Business Intelligence.*
