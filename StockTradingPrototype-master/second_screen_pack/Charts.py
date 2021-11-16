import sys

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go
import pandas as pd


class CandleStickInstance(QWidget):
    def __init__(self, file, file_type="csv", widget_width=600, widget_height=400, parent=None):
        super(CandleStickInstance, self).__init__(parent)
        self.widget_width = widget_width
        self.widget_height = widget_height
        if file_type == "csv":
            html_file = self.generate_candle_stick(self.get_df_from_csv(file))
        else:
            # if not csv then it is considered as pd.DataFrame()
            html_file = self.generate_candle_stick(file)

        self.setup_candlestick_in_current_widget(html_file)
        self.setMinimumSize(self.widget_width, self.widget_height)

    def get_df_from_csv(self, file_name):
        df = pd.read_csv(file_name)
        print(df)
        return df

    def generate_candle_stick(self, df):
        fig = go.Figure(data=[go.Candlestick(x=df['time'],
                                             open=df['open'], high=df['high'],
                                             low=df['low'], close=df['close']

                                             )])
        fig.update_layout(xaxis_rangeslider_visible=False)
        return fig.to_html(include_plotlyjs="cdn")  # cdn - Requires internet connection to display

    def setup_candlestick_in_current_widget(self, html_file):
        self.browser = QWebEngineView(self)
        self.browser.setContentsMargins(0, 0, 0, 0)
        v_layout = QVBoxLayout(self)
        v_layout.setSpacing(0)
        v_layout.addWidget(self.browser)
        self.setLayout(v_layout)
        self.browser.setHtml(html_file)


class LineChartInstance(QWidget):
    def __init__(self, file, file_type="csv", widget_width=600, widget_height=400, parent=None):
        super(LineChartInstance, self).__init__(parent)
        self.widget_width = widget_width
        self.widget_height = widget_height
        print(file)
        if file_type == "csv":
            html_file = self.generate_line_chart(self.get_df_from_csv(file))
        else:
            # if not csv then it is considered as pd.DataFrame()
            html_file = self.generate_line_chart(file)
        self.setup_linechart_in_current_widget(html_file)
        self.setMinimumSize(self.widget_width, self.widget_height)

    def get_df_from_csv(self,file_name):
        df = pd.read_csv(file_name)
        return df

    def generate_line_chart(self, df):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df['time'],
                y=df['volume']
            ))
        return fig.to_html(include_plotlyjs="cdn")  # cdn - Requires internet connection to display

    def setup_linechart_in_current_widget(self, html_file):
        # display_widget.setMaximumSize(self.widget_width, self.widget_height)
        self.browser = QWebEngineView(self)
        self.browser.setContentsMargins(0, 0, 0, 0)
        v_layout = QVBoxLayout(self)
        v_layout.setSpacing(0)
        v_layout.addWidget(self.browser)
        self.setLayout(v_layout)
        self.browser.setHtml(html_file)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ins = LineChartInstance(file=pd.read_csv("../sample_data/sample-candlestick-data.csv"), file_type="df")
    ins.show()
    app.exec()
