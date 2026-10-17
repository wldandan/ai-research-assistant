"""独立参考答案；先尝试修改 starter.py，不要只切换 solution。"""


def route_after_search(state: dict) -> str:
    if state.get('error'):
        return 'error'
    return 'report' if state.get('evidence') else 'insufficient'
