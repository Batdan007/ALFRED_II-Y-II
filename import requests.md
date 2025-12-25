import requests
# Define API key and endpoint
api_key = 'YOUR_API_KEY'
symbol = 'AAPL'
url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
# Make the API request
response = requests.get(url)
data = response.json()
# Extract and display the stock price
quote = data['Global Quote']
print(f"The current price of {symbol} is {quote['05. price']}")