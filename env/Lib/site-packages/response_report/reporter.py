import json
import urllib.parse
from typing import Union

from requests import Response as r_Response
from httpx._models import Response as h_Response


class Reporter:
    def __init__(self, response: Union[r_Response, h_Response]):
        """
        Class for generate response report

        :param response: (requests or) httpx Response
        """
        lines = []
        steps: list[h_Response] = response.history + [response]
        for index, step in enumerate(steps):
            lines.append(''.center(52, "#"))
            lines.append(f' STEP {index + 1} '.center(52, "#"))
            lines.append(''.center(52, "#"))
            lines.append('')
            lines.append(f'R-URL: {step.request.url}')
            lines.append(f'URL: {step.url}')
            lines.append(f'Code: {step.status_code} {step.reason_phrase}')
            lines.append(f'Method: {step.request.method}')
            lines.append('')
            lines.append(' REQUEST '.center(52, "#"))
            lines.append('Headers:')
            lines.append('')
            for k, v in step.request.headers.raw:
                lines.append(f'{k.decode()}: '.ljust(16, " ") + v.decode())
            lines.append('')
            if step.request.headers['content-type'] == 'application/x-www-form-urlencoded':
                x = [urllib.parse.unquote(i) for i in step.request.content.decode().split("&")]
                lines.append(f' CONTENT '.center(32, "#"))
                lines.extend(x)
                lines.append(' END CONTENT '.center(32, "#"))
                lines.append('')
            elif step.request.headers['content-type'] == 'application/json':
                try:
                    x = json.dumps(json.loads(step.request.content), indent=4, sort_keys=True)
                    lines.append(f' CONTENT '.center(32, "#"))
                    lines.append(x)
                    lines.append(' END CONTENT '.center(32, "#"))
                    lines.append('')
                except:
                    lines.append(f' CONTENT '.center(32, "#"))
                    lines.append(step.request.content.decode())
                    lines.append(' END CONTENT '.center(32, "#"))
                    lines.append('')
            elif step.request.content:
                lines.append(f' CONTENT '.center(32, "#"))
                lines.append(step.request.content.decode())
                lines.append(' END CONTENT '.center(32, "#"))
                lines.append('')
            lines.append(' RESPONSE '.center(52, "#"))
            lines.append('')
            lines.append('Headers:')
            lines.append('')
            for k, v in step.headers.raw:
                lines.append(f'{k.decode()}: '.ljust(16, " ") + v.decode())
            if step.text:
                lines.append('')
                content_lines = step.text.count("\n")
                lines.append(f' CONTENT '.center(32, "#"))
                lines.append(step.text)
                lines.append(' END CONTENT '.center(32, "#"))
                lines.append('')
        self.lines = [line + "\n" for line in lines]

    def save(self, name: str) -> str:
        """

        :param name: filename
        :return: report-str
        """
        with open(name, "w+") as rf:
            rf.writelines(self.lines)
        return "".join(self.lines)




