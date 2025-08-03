import sqlite3
import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('trades.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    trades_df = pd.read_sql_query("SELECT * FROM trades ORDER BY entry_timestamp DESC", conn)
    conn.close()

    # Calculate some basic stats for the dashboard
    if not trades_df.empty:
        total_trades = len(trades_df)
        wins = trades_df[trades_df['pnl'] > 0]
        win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
        total_pnl = trades_df['pnl'].sum()
        profit_factor = trades_df[trades_df['pnl'] > 0]['pnl'].sum() / abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())
    else:
        total_trades, win_rate, total_pnl, profit_factor = 0, 0, 0, 0

    stats = {
        "total_trades": total_trades,
        "win_rate": f"{win_rate:.2f}%",
        "total_pnl": f"${total_pnl:,.2f}",
        "profit_factor": f"{profit_factor:.2f}"
    }

    # Convert dataframe to list of dicts for easy rendering in template
    trades = trades_df.to_dict(orient='records')

    return render_template('dashboard.html', stats=stats, trades=trades)

if __name__ == '__main__':
    print("Starting Flask dashboard. Go to http://127.0.0.1:5000 in your browser.")
    app.run(debug=True)
