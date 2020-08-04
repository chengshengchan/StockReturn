"""The index page."""

import applications
import layouts
from callbacks import *


app = applications.app
app.layout = layouts.main_page

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8888, debug=True)
