print("Before import")
import webview
print("After import")
webview.create_window('Hello world', 'https://pywebview.flowrl.com/')
print("Created window")
webview.start(debug=True)
print("Closed window")
