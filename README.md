# wishlist-price-checker

Checks every hour (via cron) if Amazon wishlist item prices have changed.

### Running

0. Set up python-amazon-product-api (See below)
1. Create the database and table using `database.sql`
2. Edit `sample_config.py` and rename to `config.py`
3. Run!

### How do I get my Amazon Wishlist ID?

Go to the Amazon app or website, open your list, and share it. The list must be public to work. The list url will be similar to "https://amazon.com/registry/wishlist/<ID HERE>". Or, "https://amzn.com/w/<ID HERE>". Put this ID in your `config.py`.

### How do I set up python-amazon-product-api?

Instructions can be found on the project's [BitBucket page](https://bitbucket.org/basti/python-amazon-product-api/overview) under "Basic Usage". You will need to create a `~/.amazon-product-api` file with credentials.
