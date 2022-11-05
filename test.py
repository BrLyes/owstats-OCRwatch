from ocr import process_screenshot_file
from output import write_output

print("start testing")
result = process_screenshot_file(f"monitor-4.png")
write_output(result)