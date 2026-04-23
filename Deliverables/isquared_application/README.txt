BACKEND QUERIES IMPLEMENTATION: VERSION NOTES (IVAN):

Overview:
The following changes were implemented in this version:
 - Fixed dataset issues (review table expanded from 32 loaded rows to the full dataset 416k rows)

Updates:
 - 'numCheckins' using checkin aggr
 - 'reveiwRating' using review averages
 - Implementation of parametrized SQL Queries:
   - Popular Business (based on check-ins and review count)
   - Successful Business (based on rating, reviews, and check-ins)

Query Implementation Details:

# Popular Businesses
Returns businesses with:
- Above-average check-ins
- Above-average review count

# Successful Businesses
Returns businesses with:
- Above-average rating
- Above-average review count
- Above-average check-ins

# Technologies Used
- Python (PyQt6)
- PostgreSQL
- psycopg2

# Notes
- All SQL queries are parameterized to prevent SQL injection.
- Data was cleaned and validated before use.
- Backend functions are ready for UI integration.

# How to Run
```bash
py milstone1.py

-------------------------------------------------------------------------------------------------------------
# Prerequisites

Before running this application, you should have the following installed and configured:

- Python 3.x (tested with Python 3.14.3)
- PostgreSQL (running locally)
- A PostgreSQL database named:
  - `milestone1db`
  - fully populated tables and required components
- Required Python packages:
  - `PyQt6`
  - `psycopg2-binary`

# Python Setup

Install required packages using:

```bash
pip install PyQt6 psycopg2-binary

