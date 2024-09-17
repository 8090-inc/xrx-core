---
sidebar_position: 1
---

# Run the Shopify Application

This application allows you to chat and interact with Shopify stores. There are two sample UIs in the application: a pizza store and an apparel store. It requires you to have a Shopify shop and API credentials. 

## Store Configuration

To get started with the quick service restaurant agent, you need to create a Shopify shop.

### Sign Up for Shopify and Create a Shop

Go to the [Shopify website](https://www.shopify.com/) and sign up for a new account by clicking [Start free trial](https://accounts.shopify.com/shop-create?language=en&locale=en). Follow the on-screen instructions to set up your shop. You can learn more on the [Shopify getting started](https://help.shopify.com/en/manual/intro-to-shopify/initial-setup/setup-getting-started) page. For this tutorial, a blank shop is all you will need to continue.

### Import Products
As soon as you create the store, Shopify will ask you to import some products. You can make your own products, or you can use the products we have provided in the `config/shopify/pizza-store.csv` file [here](https://github.com/8090-inc/xrx/tree/main/config/shopify/pizza-store.csv).

If you skipped the onboarding and you have no products in the store, do the following: to import the products to your shop, navigate to the admin link of your Shopify Shop (https://admin.shopify.com/store/SHOP_NAME) and click on **Products** in the left-hand menu. Then click on **Import** and upload the `pizza-store.csv` file from your computer.

### Generate API Credentials

In this section, we will generate four specific Shopify variables which are needed for the xRx Shopify agent: `SHOPIFY_API_KEY`, `SHOPIFY_TOKEN`, `SHOPIFY_SHOP`, and `SHOPIFY_SHOP_GID`.

Start by configuring the API scopes for your shop

* Navigate to the Shopify admin panel. This will be a url like `https://admin.shopify.com/store/{your_shop_name}`.
* Go to **Settings** and click on **Apps and sales channels**.
* Click on **Develop apps**.
* Click on **Allow custom app development**, and again click on **Allow custom app development**.
* Click on **Create an app**.
* Enter a name for your app, such as `xRx App` and click on **Create app**.
* On the next page, click on **Configure Admin API scopes**.
* Select the **Read and write** option and click on **Continue**.
* In the example solution, the minimum scopes are `read_products`, `write_draft_orders`, `read_draft_orders`, `write_orders`, and `read_orders`.
* Scroll down and click on **Save**.

Next you need to generate your API key, token, and shop name (`SHOPIFY_API_KEY`, `SHOPIFY_TOKEN`, `SHOPIFY_SHOP`).

* Go to the **API credentials** tab.
* Scroll down to API key and secret key, and note down the "API key" This is the `SHOPIFY_API_KEY`.
* Click on **Install app** to generate an access token.
* Click on **Reveal token once** and note down the `SHOPIFY_TOKEN`. It should start with `shpat_`.
  * **WARNING: YOU WILL ONLY BE ABLE TO SEE THE TOKEN ONCE, SO MAKE SURE TO WRITE IT DOWN!** 
* On the upper left of the screen, you should see the url for the shop. For example, abc123-def.myshopify.com. Note down the first part of the url, for example, abc123-def. This is the `SHOPIFY_SHOP`.
  
Lastly, you need your shop's global identifier (`SHOPIFY_SHOP_GID`). This is a bit harder to find. 

**Option 1:** use the Shopify admin api. Here is a curl command which you can run to get the shop's global ID. Note that the `SHOPIFY_TOKEN` is the same as the one you generated above and the `SHOPIFY_SHOP` is the same as the one you noted down. This command will produce a JSON object which contains a string that says "gid://shopify/Shop/1234". The `1234` is the global ID.

```bash
curl -X POST \
    -H "X-Shopify-Access-Token: $SHOPIFY_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"query": "{ shop { id } }"}' \
    "https://$SHOPIFY_SHOP.myshopify.com/admin/api/2023-07/graphql.json"
```

**Option 2:** go to the shop admin page, create an order, go to the order page and the url in the address bar will be in the format of `https://shopify.com/123456789/account/orders/ABCD5678`. The `123456789` is the global ID `SHOPIFY_SHOP_GID`.

*Important Check: if you do not have your `SHOPIFY_API_KEY`, `SHOPIFY_TOKEN`, `SHOPIFY_SHOP`, and `SHOPIFY_SHOP_GID` ready, please return to the top of this section and continue from there.*

### Set up the .env file

If you have already configured xRx with a `.env` file, skip this step. If you are new to xRx, you just need to activate and update the `.env` example present in the Shopify agent application folder.

Update the .env file with the following:

* Update the `SHOPIFY_API_KEY`, `SHOPIFY_TOKEN`, `SHOPIFY_SHOP`, and `SHOPIFY_SHOP_GID` environment variables with the values you noted down in the above steps.
* Update the additional environment variables. Documentation on this can be found in the [Quick Start](/docs/quickstart) section.
* Update the `NEXT_PUBLIC_UI` variable with either `"pizza-agent"` or `"shoe-agent"` depending on your store.
* Update the `SHOPIFY_STORE_INFO` with the name of your shop. This is what the agent will refer to your shop as. We recommend, `Shoe Shop` based on the products we will be using in this example.
* Update the `SHOPIFY_CUSTOMER_SERVICE_TASK` with the task you want the agent to perform. For example:
  ```
  SHOPIFY_CUSTOMER_SERVICE_TASK="You are a customer service representative who is 
  helping customers order items from the shop. You are courteous, helpful and concise."
  ```

## Check Redis Integration

*No action is needed for this section if you are using the docker-compose setup and pre-provided `.env` file.*

The quick service restaurant agent uses a Redis container (xrx-redis) to shop and manage task statuses. This allows for efficient, real-time status updates and checks across the distributed system.

If you are using the docker-compose setup, the Redis container will be automatically started and the reasoning agent will be able to use it as long as the environment variable is correctly set as shown below.

```
REDIS_HOST="xrx-redis"
```

If you are running the agent locally outside of docker compose, the reasoning agent will look for a Redis container on the default host (`localhost`) and port (`6379`). In order to start that server, you can use the following command:

```
docker run -d --name redis-server -p 6379:6379 redis
```

## Deploy the Containers

Once you have completed the above steps, you can deploy the containers by running the following command:

```
docker compose up --build
```

Enjoy experimenting!
