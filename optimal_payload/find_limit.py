# Example of use:
# limit = FIND_LIMIT(url, max_value, timeout, limit_parameter_name, **parameters)

class FIND_LIMIT:
    def __init__(
            self, 
            url, 
            max_value=10_000, 
            timeout=2, 
            limit_parameter_name="limit", 
            **parameters
    ) -> None:
        self.find(url, max_value, timeout, limit_parameter_name, **parameters)
        
    def _valid_url(url, limit_parameter_name, limit_value, **kwargs):
        import requests
        
        kwargs[limit_parameter_name] = limit_value
        url = str(url) + "&".join([f"{key}={value}" for key, value in kwargs.items()])
        response = requests.get(url)
        return response.ok

    def _generate_adjustments(n):
        n = int('1' + (len(str(n)) - 1) * '0')
        l = []
        while (n > 1):
            n //= 2    
            l.append(n)
            n //= 5
            l.append(n)
        return l

    def find(self, url, max_value, timeout, limit_parameter_name, **parameters):
        import time
        
        n = max_value
        adjustments = self._generate_adjustments(n)
        valid_limit = lambda limit_value: self._valid_url(
            url, 
            limit_parameter_name, 
            limit_value, 
            **parameters
        )
        s = set()
        prev_len = None

        for index in range(len(adjustments)):
            if valid_limit(n):
                while valid_limit(n):  
                    time.sleep(timeout)                
                    prev_len = len(s)
                    n += adjustments[index]
                    s.add(n)
                    if prev_len == len(s): continue
            else:
                while not valid_limit(n):
                    time.sleep(timeout)                
                    prev_len = len(s)
                    n -= adjustments[index]
                    s.add(n)
                    if prev_len == len(s): continue                    
        return n - 1
