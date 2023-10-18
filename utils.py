import io
import base64
import pandas as pd

def decode_contents(contents):
    content_type, content_string = contents.split(',')
    decoded_content = base64.b64decode(content_string)
    decoded = pd.read_csv(io.StringIO(decoded_content.decode('utf-8')))
    return decoded
