from chart_generator_tool.tool import TradingChartTool
from crewai.tools import tool, BaseTool

_instance = TradingChartTool()

@tool("TradingChartTool")
def trading_chart_tool(
    asset: str,
    direction: str,
    entry: float,
    stop_loss: float,
    take_profit_1: float,
    take_profit_2: float = None,
    setup_type: str = "Setup",
    timeframe: str = "1H",
    confidence: int = 75,
    telegram_chat_id: str = ""
) -> str:
    """Generates a professional dark-theme trading setup chart and sends it via Telegram."""
    return _instance._run(
        asset=asset, direction=direction, entry=entry,
        stop_loss=stop_loss, take_profit_1=take_profit_1,
        take_profit_2=take_profit_2, setup_type=setup_type,
        timeframe=timeframe, confidence=str(confidence),
        telegram_chat_id=telegram_chat_id
    )

__all__ = ['TradingChartTool', 'trading_chart_tool', 'BaseTool']
