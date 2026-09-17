import os
import io
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class ChartInput(BaseModel):
    asset: str = Field(..., description="Asset name, e.g. 'EUR/USD', 'BTC/USD', 'S&P 500'")
    direction: str = Field(..., description="Trade direction: 'LONG' or 'SHORT'")
    entry: float = Field(..., description="Entry price level")
    stop_loss: float = Field(..., description="Stop-loss price level")
    take_profit_1: float = Field(..., description="First take-profit level (TP1)")
    take_profit_2: Optional[float] = Field(None, description="Second take-profit level (TP2), optional")
    setup_type: Optional[str] = Field("", description="Setup type, e.g. 'Breakout', 'Reversal'")
    timeframe: Optional[str] = Field("", description="Timeframe, e.g. '4H', 'Daily'")
    confidence: Optional[str] = Field("", description="Confidence level, e.g. '75%'")
    telegram_chat_id: str = Field(..., description="Telegram chat ID to send the chart image to")


class TradingChartTool(BaseTool):
    name: str = "trading_chart_generator"
    description: str = (
        "Generates a professional dark-theme trading setup chart showing entry, "
        "stop-loss and take-profit levels with colored risk/reward zones, "
        "then sends the chart image directly to a Telegram chat. "
        "Use this after identifying a trading setup to visually communicate it. "
        "Returns confirmation with Telegram message ID on success, or an error description."
    )
    args_schema: Type[BaseModel] = ChartInput

    def _run(
        self,
        asset: str,
        direction: str,
        entry: float,
        stop_loss: float,
        take_profit_1: float,
        take_profit_2: Optional[float] = None,
        setup_type: Optional[str] = "",
        timeframe: Optional[str] = "",
        confidence: Optional[str] = "",
        telegram_chat_id: str = "",
    ) -> str:
        try:
            # Invio dati JSON alla Dashboard API
            self._send_to_dashboard({
                "asset": asset,
                "direction": direction,
                "entry": entry,
                "stop_loss": stop_loss,
                "take_profit_1": take_profit_1,
                "take_profit_2": take_profit_2,
                "setup_type": setup_type,
                "timeframe": timeframe,
                "confidence": confidence
            })

            img_bytes = self._generate_chart(
                asset, direction, entry, stop_loss,
                take_profit_1, take_profit_2,
                setup_type or "", timeframe or "", confidence or ""
            )
            return self._send_to_telegram(img_bytes, asset, direction, telegram_chat_id)
        except Exception as e:
            return f"ERROR generating or sending chart: {str(e)}"

    def _send_to_dashboard(self, data):
        import requests
        try:
            requests.post("http://localhost:4000/api/signals", json=data, timeout=5)
        except Exception as e:
            print(f"Warning: Could not send to dashboard: {e}")

    def _generate_chart(
        self,
        asset,
        direction,
        entry,
        stop_loss,
        take_profit_1,
        take_profit_2,
        setup_type,
        timeframe,
        confidence,
    ):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches

        is_long = direction.upper() == "LONG"

        levels = [entry, stop_loss, take_profit_1]
        if take_profit_2:
            levels.append(take_profit_2)

        price_range = max(levels) - min(levels)
        if price_range == 0:
            price_range = abs(entry) * 0.02
        margin = price_range * 0.45
        y_min = min(levels) - margin
        y_max = max(levels) + margin

        risk = abs(entry - stop_loss)
        rr1 = round(abs(take_profit_1 - entry) / risk, 2) if risk > 0 else "N/A"
        rr2 = round(abs(take_profit_2 - entry) / risk, 2) if take_profit_2 and risk > 0 else None

        fig, ax = plt.subplots(figsize=(11, 7))
        fig.patch.set_facecolor('#0d1117')
        ax.set_facecolor('#0d1117')

        # Colored zones
        if is_long:
            ax.axhspan(stop_loss, entry, alpha=0.18, color='#ff4444', zorder=1)
            ax.axhspan(entry, take_profit_1, alpha=0.14, color='#00ff88', zorder=1)
            if take_profit_2:
                ax.axhspan(take_profit_1, take_profit_2, alpha=0.09, color='#00cc66', zorder=1)
        else:
            ax.axhspan(entry, stop_loss, alpha=0.18, color='#ff4444', zorder=1)
            ax.axhspan(take_profit_1, entry, alpha=0.14, color='#00ff88', zorder=1)
            if take_profit_2:
                ax.axhspan(take_profit_2, take_profit_1, alpha=0.09, color='#00cc66', zorder=1)

        # Price lines
        line_defs = [
            (entry, '#FFD700', 2.8, f'ENTRY  {entry:,.5f}', 'solid'),
            (stop_loss, '#FF4444', 2.2, f'STOP LOSS  {stop_loss:,.5f}  [-{risk:,.5f}]', 'dashed'),
            (take_profit_1, '#00FF88', 2.2, f'TP1  {take_profit_1:,.5f}  (R:R 1:{rr1})', 'dashed'),
        ]
        if take_profit_2:
            line_defs.append(
                (take_profit_2, '#00CC66', 1.8, f'TP2  {take_profit_2:,.5f}  (R:R 1:{rr2})', 'dotted')
            )

        for price, color, lw, label, ls in line_defs:
            ax.axhline(y=price, color=color, linewidth=lw, linestyle=ls, alpha=0.92, zorder=2)
            ax.text(
                0.015, price, f'  {label}',
                transform=ax.get_yaxis_transform(),
                color=color, fontsize=8.5, fontweight='bold', va='center',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#0d1117', alpha=0.75, edgecolor='none')
            )

        # Direction arrow
        arrow_color = '#00FF88' if is_long else '#FF4444'
        arrow_dir = 1 if is_long else -1
        mid_x = 0.82
        ax.annotate(
            '', xy=(mid_x, entry + arrow_dir * price_range * 0.18),
            xytext=(mid_x, entry - arrow_dir * price_range * 0.08),
            xycoords=('axes fraction', 'data'),
            textcoords=('axes fraction', 'data'),
            arrowprops=dict(arrowstyle='->', color=arrow_color, lw=3.0)
        )

        # Title
        dir_label = 'LONG' if is_long else 'SHORT'
        parts = [f'{asset}', dir_label]
        if setup_type:
            parts.append(setup_type)
        if timeframe:
            parts.append(timeframe)
        if confidence:
            parts.append(f'Conf. {confidence}')
        ax.set_title('  |  '.join(parts), color='white', fontsize=13, fontweight='bold', pad=14)

        ax.set_ylim(y_min, y_max)
        ax.set_xlim(0, 1)
        ax.set_xticks([])
        ax.yaxis.tick_right()
        ax.tick_params(axis='y', colors='#888888', labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor('#2a2a2a')

        # Legend
        patches = [
            mpatches.Patch(color='#FFD700', label='Entry'),
            mpatches.Patch(color='#FF4444', label='Stop Loss (Risk)'),
            mpatches.Patch(color='#00FF88', label='TP1 (Reward)'),
        ]
        if take_profit_2:
            patches.append(mpatches.Patch(color='#00CC66', label='TP2 (Extended)'))
        ax.legend(
            handles=patches, loc='lower right' if is_long else 'upper right',
            facecolor='#1a1a2e', edgecolor='#333333',
            labelcolor='white', fontsize=8.5, framealpha=0.9
        )

        ax.text(
            0.5, 0.005, 'QuantitativeMarketAnalyst — Paper Trading Flow',
            transform=ax.transAxes, color='#3a3a3a', fontsize=6.5, ha='center'
        )

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    def _send_to_telegram(self, img_bytes, asset, direction, chat_id):
        import requests

        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if not token:
            return "ERROR: TELEGRAM_BOT_TOKEN environment variable is not set. Add it in the platform settings."

        caption = f"\U0001f4ca Setup: {asset} {direction.upper()}"
        url = f"https://api.telegram.org/bot{token}/sendPhoto"

        try:
            response = requests.post(
                url,
                data={"chat_id": chat_id, "caption": caption},
                files={"photo": ("setup_chart.png", img_bytes, "image/png")},
                timeout=30
            )
        except requests.exceptions.Timeout:
            return "ERROR: Telegram API request timed out after 30 seconds."
        except requests.exceptions.RequestException as e:
            return f"ERROR: Network error when calling Telegram API: {str(e)}"

        if response.status_code == 200:
            msg_id = response.json().get("result", {}).get("message_id", "unknown")
            return f"Chart sent successfully to Telegram chat {chat_id}. Message ID: {msg_id}."
        else:
            return f"ERROR from Telegram API: HTTP {response.status_code} — {response.text}"