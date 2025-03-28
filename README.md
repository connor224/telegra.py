# telegra.py

A Python client for the Telegraph API (https://telegra.ph/api).

Telegra.ph is a minimalist publishing tool that allows you to create richly formatted posts and push them to the Web in just a click. This library provides a simple and asynchronous way to interact with the Telegraph API from your Python applications.

## Installation

```bash
pip install aiohttp attrs yarl
```

Or, if you want to install directly from GitHub:

```bash
pip install git+https://github.com/connor224/telegra.py.git
```

## Usage

To use this library, you'll need to install the required dependencies: `aiohttp`, `attrs`, and `yarl`.

Here's a basic example of how to use the library:

```python
import asyncio
import telegra

async def main():
    telegraph = telegra.Telegraph()
    try:
        account = await telegraph.createAccount(short_name="My Account")
        print(f"Account: {account}")
        print(f"Account auth_url: {account.auth_url}")

        access_token = account.access_token

        edited_account = await telegraph.editAccountInfo(
            access_token=access_token, author_name="New Author Name"
        )
        print(f"Edited Account: {edited_account}")
        print(f"Edited Account author_name: {edited_account.author_name}")

        account_info = await telegraph.getAccountInfo(
            access_token=access_token, fields=["short_name", "page_count"]
        )
        print(f"Account Info: {account_info}")
        print(f"Account Info page_count: {account_info.page_count}")

        content = [
            "Hello, world!",
            telegra.NodeElement(tag="b", children=["This is bold text."]),
            telegra.NodeElement(tag="img", attrs={"src": "https://example.com/image.jpg"}),
            telegra.NodeElement(tag="iframe", attrs={"src": "https://www.youtube.com/embed/dQw4w9WgXcQ"}),
        ]
        try:
            page = await telegraph.createPage(
                access_token=access_token, title="My First Page", content=content
            )
            print(f"Page: {page}")
            print(f"Page url: {page.url}")
        except ValueError as e:
            print(f"Validation Error: {e}")

        if page:
            edited_page = await telegraph.editPage(
                access_token=access_token,
                path=page.path,
                title="My Edited Page",
                content=["This page has been edited!"],
            )
            print(f"Edited Page: {edited_page}")

            retrieved_page = await telegraph.getPage(path=page.path, return_content=True)
            print(f"Retrieved Page content: {retrieved_page.content}")

            page_list = await telegraph.getPageList(access_token=access_token, limit=2)
            print(f"Page List total_count: {page_list.total_count}")

            page_views = await telegraph.getViews(path=page.path)
            print(f"Page Views: {page_views.views}")

        telegraph.account = account
        revoked_account = await telegraph.revokeAccessToken(access_token=access_token)
        print(f"Revoked Account access_token: {revoked_account.access_token}")

    except telegra.TelegraphError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

All queries to the Telegraph API must be served over HTTPS.

### Methods

*   [createAccount](#createaccount)
*   [editAccountInfo](#editaccountinfo)
*   [getAccountInfo](#getaccountinfo)
*   [revokeAccessToken](#revokeaccesstoken)
*   [createPage](#createpage)
*   [editPage](#editpage)
*   [getPage](#getpage)
*   [getPageList](#getpagelist)
*   [getViews](#getviews)

### Types

*   [Account](#account)
*   [NodeElement](#nodeelement)
*   [Page](#page)
*   [PageList](#pagelist)
*   [PageViews](#pageviews)

### Content Format

The Telegraph API uses a DOM-based format to represent the content of the page. See the [NodeElement](#nodeelement) section for details.

---

<a name="createaccount"></a>

#### createAccount

Use this method to create a new Telegraph account. Most users only need one account, but this can be useful for channel administrators who would like to keep individual author names and profile links for each of their channels. On success, returns an [Account](#account) object with the regular fields and an additional `access_token` field.

*   **Parameters:**

    *   `short_name` (*str*, required): Account name (1-32 characters). Helps users with several accounts remember which they are currently using. Displayed to the user above the "Edit/Publish" button on Telegra.ph; other users don't see this name.
    *   `author_name` (*str*, optional): Default author name used when creating new articles (0-128 characters).
    *   `author_url` (*str*, optional): Default profile link, opened when users click on the author's name below the title. Can be any link, not necessarily to a Telegram profile or channel (0-512 characters).

*   **Example:**

    ```python
    import asyncio
    import telegra

    async def main():
        telegraph = telegra.Telegraph()
        try:
            account = await telegraph.createAccount(short_name="My Account", author_name="John Doe", author_url="https://example.com")
            print(f"Account: {account}")
            print(f"Access Token: {account.access_token}")
        except telegra.TelegraphError as e:
            print(f"Error: {e}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

*   **Expected Result:**

    An `Account` object with the following attributes: `short_name`, `author_name`, `author_url`, `access_token`, and `auth_url`.

<a name="editaccountinfo"></a>

#### editAccountInfo

Use this method to update information about a Telegraph account. Pass only the parameters that you want to edit. On success, returns an [Account](#account) object with the default fields.

*   **Parameters:**

    *   `access_token` (*str*, required): Access token of the Telegraph account.
    *   `short_name` (*str*, optional): New account name (1-32 characters).
    *   `author_name` (*str*, optional): New default author name used when creating new articles (0-128 characters).
    *   `author_url` (*str*, optional): New default profile link (0-512 characters).

*   **Example:**

    ```python
    import asyncio
    import telegra

    async def main():
        telegraph = telegra.Telegraph()
        try:
            account = await telegraph.createAccount(short_name="My Account")
            access_token = account.access_token

            edited_account = await telegraph.editAccountInfo(access_token=access_token, author_name="Jane Doe")
            print(f"Edited Account: {edited_account}")
            print(f"New Author Name: {edited_account.author_name}")
        except telegra.TelegraphError as e:
            print(f"Error: {e}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

*   **Expected Result:**

    An `Account` object with the updated attributes.

<a name="getaccountinfo"></a>

#### getAccountInfo

Use this method to get information about a Telegraph account. Returns an [Account](#account) object on success.

*   **Parameters:**

    *   `access_token` (*str*, required): Access token of the Telegraph account.
    *   `fields` (*list[str]*, optional): List of account fields to return. Available fields: `"short_name"`, `"author_name"`, `"author_url"`, `"auth_url"`, `"page_count"`. Defaults to `["short_name", "author_name", "author_url"]`.

*   **Example:**

    ```python
    import asyncio
    import telegra

    async def main():
        telegraph = telegra.Telegraph()
        try:
            account = await telegraph.createAccount(short_name="My Account")
            access_token = account.access_token

            account_info = await telegraph.getAccountInfo(access_token=access_token, fields=["short_name", "page_count"])
            print(f"Account Info: {account_info}")
            print(f"Page Count: {account_info.page_count}")
        except telegra.TelegraphError as e:
            print(f"Error: {e}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

*   **Expected Result:**

    An `Account` object with the requested fields.

<a name="revokeaccesstoken"></a>

#### revokeAccessToken

Use this method to revoke `access_token` and generate a new one, for example, if the user would like to reset all connected sessions, or you have reasons to believe the token was compromised. On success, returns an [Account](#account) object with new `access_token` and `auth_url` fields.

*   **Parameters:**

    *   `access_token` (*str*, required): Access token of the Telegraph account.

*   **Example:**

    ```python
    import asyncio
    import telegra

    async def main():
        telegraph = telegra.Telegraph()
        try:
            account = await telegraph.createAccount(short_name="My Account")
            access_token = account.access_token

            revoked_account = await telegraph.revokeAccessToken(access_token=access_token)
            print(f"Revoked Account: {revoked_account}")
            print(f"New Access Token: {revoked_account.access_token}")
        except telegra.TelegraphError as e:
            print(f"Error: {e}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

*   **Expected Result:**

    An `Account` object with the new `access_token` and `auth_url`.

<a name="createpage"></a>

#### createPage

Use this method to create a new Telegraph page. On success, returns a [Page](#page) object.

*   **Parameters:**

    *   `access_token` (*str*, required): Access token of the Telegraph account.
    *   `title` (*str*, required): Page title (1-256 characters).
    *   `content` (*list[Union[str, NodeElement]]*, required): [Content](#content-format) of the page (up to 64 KB).
    *   `author_name` (*str*, optional): Author name, displayed below the article's title (0-128 characters).
    *   `author_url` (*str*, optional): Profile link, opened when users click on the author's name below the title. Can be any link, not necessarily to a Telegram profile or channel (0-512 characters).
    *   `return_content` (*bool*, optional): If `True`, a `content` field will be returned in the [Page](#page) object. Defaults to `False`.

*   **Example:**

    ```python
    import asyncio
    import telegra

    async def main():
        telegraph = telegra.Telegraph()
        try:
            account = await telegraph.createAccount(short_name="My Account")
            access_token = account.access_token

            content = [
                "Hello, world!",
                telegra.NodeElement(tag="b", children=["This is bold text."]),
                telegra.NodeElement(tag="img", attrs={"src": "https://example.com/image.jpg"}),
            ]
            page = await telegraph.createPage(
                access_token=access_token, title="My First Page", content=content, return_content=True
            )
            print(f"Page: {page}")
            print(f"Page Content: {page.content}")
        except telegra.TelegraphError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Validation Error: {e}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

*   **Expected Result:**

    A `Page` object with the following attributes: `path`, `url`, `title`, `description`, `author_name`, `author_url`, `image_url`, `content` (if `return_content` is `True`), `views`, and `can_edit`.

<a name="editpage"></a>

#### editPage

Use this method to edit an existing Telegraph page. On success, returns a [Page](#page) object.

*   **Parameters:**

    *   `access_token` (*str*, required): Access token of the Telegraph account.
    *   `path` (*str*, required): Path to the page.
    *   `title` (*str*, required): Page title (1-256 characters).
    *   `content` (*list[Union[str, NodeElement]]*, required): [Content](#content-format) of the page (up to 64 KB).
    *   `author_name` (*str*, optional): Author name, displayed below the article's title (0-128 characters).
    *   `author_url` (*str*, optional): Profile link (0-512 characters).
    *   `return_content` (*bool*, optional): If `True`, a `content` field will be returned in the [Page](#page) object. Defaults to `False`.

*   **Example:**

    ```python
    import asyncio
    import telegra

    async def main():
        telegraph = telegra.Telegraph()
        try:
            account = await telegraph.createAccount(short_name="My Account")
            access_token = account.access_token

            content = [
                "Hello, world!",
                telegra.NodeElement(tag="b", children=["This is bold text."]),
                telegra.NodeElement(tag="img", attrs={"src": "https://example.com/image.jpg"}),
            ]
            page = await telegraph.createPage(
                access_token=access_token, title="My First Page", content=content
            )

            edited_page = await telegraph.editPage(
                access_token=access_token, path=page.path, title="My Edited Page", content=["This page has been edited!"]
            )
            print(f"Edited Page: {edited_page}")
        except telegra.TelegraphError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Validation Error: {e}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

*   **Expected Result:**

    A `Page` object with the updated attributes.

<a name="getpage"></a>

#### getPage

Use this method to get a Telegraph page. Returns a [Page](#page) object on success.

*   **Parameters:**

    *   `path` (*str*, required): Path to the Telegraph page (in the format `Title-12-31`, i.e., everything that comes after `http://telegra.ph/`).
    *   `return_content` (*bool*, optional): If `True`, `content` field will be returned in [Page](#page) object. Defaults to `False`.

*   **Example:**

    ```python
    import asyncio
    import telegra

    async def main():
        telegraph = telegra.Telegraph()
        try:
            account = await telegraph.createAccount(short_name="My Account")
            access_token = account.access_token

            content = [
                "Hello, world!",
                telegra.NodeElement(tag="b", children=["This is bold text."]),
                telegra.NodeElement(tag="img", attrs={"src": "https://example.com/image.jpg"}),
            ]
            page = await telegraph.createPage(
                access_token=access_token, title="My First Page", content=content
            )

            retrieved_page = await telegraph.getPage(path=page.path, return_content=True)
            print(f"Retrieved Page: {retrieved_page}")
            print(f"Retrieved Page Content: {retrieved_page.content}")
        except telegra.TelegraphError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Validation Error: {e}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

*   **Expected Result:**

    A `Page` object with the requested information.

<a name="getpagelist"></a>

#### getPageList

Use this method to get a list of pages belonging to a Telegraph account. Returns a [PageList](#pagelist) object, sorted by most recently created pages first.

*   **Parameters:**

    *   `access_token` (*str*, required): Access token of the Telegraph account.
    *   `offset` (*int*, optional): Sequential number of the first page to be returned. Defaults to `0`.
    *   `limit` (*int*, optional): Limits the number of pages to be retrieved (0-200). Defaults to `50`.

*   **Example:**

    ```python
    import asyncio
    import telegra

    async def main():
        telegraph = telegra.Telegraph()
        try:
            account = await telegraph.createAccount(short_name="My Account")
            access_token = account.access_token

            page_list = await telegraph.getPageList(access_token=access_token, limit=3)
            print(f"Page List: {page_list}")
            print(f"Total Count: {page_list.total_count}")
        except telegra.TelegraphError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Validation Error: {e}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

*   **Expected Result:**

    A `PageList` object containing the `total_count` and a list of `Page` objects.

<a name="getviews"></a>

#### getViews

Use this method to get the number of views for a Telegraph article. Returns a [PageViews](#pageviews) object on success. By default, the total number of page views will be returned.

*   **Parameters:**

    *   `path` (*str*, required): Path to the Telegraph page (in the format `Title-12-31`).
    *   `year` (*int*, optional): If passed, the number of page views for the requested year will be returned (2000-2100). Required if `month` is passed.
    *   `month` (*int*, optional): If passed, the number of page views for the requested month will be returned (1-12). Required if `day` is passed.
    *   `day` (*int*, optional): If passed, the number of page views for the requested day will be returned (1-31). Required if `hour` is passed.
    *   `hour` (*int*, optional): If passed, the number of page views for the requested hour will be returned (0-24).

*   **Example:**

    ```python
    import asyncio
    import telegra

    async def main():
        telegraph = telegra.Telegraph()
        try:
            account = await telegraph.createAccount(short_name="My Account")
            access_token = account.access_token

            content = [
                "Hello, world!",
                telegra.NodeElement(tag="b", children=["This is bold text."]),
                telegra.NodeElement(tag="img", attrs={"src": "https://example.com/image.jpg"}),
            ]
            page = await telegraph.createPage(
                access_token=access_token, title="My First Page", content=content
            )

            page_views = await telegraph.getViews(path=page.path)
            print(f"Page Views: {page_views}")
            print(f"View Count: {page_views.views}")
        except telegra.TelegraphError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Validation Error: {e}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

*   **Expected Result:**

    A `PageViews` object containing the `views` count.

---

<a name="account"></a>

### Account

This object represents a Telegraph account.

*   **Fields:**

    *   `short_name` (*str*): Account name.
    *   `author_name` (*str*, optional): Default author name.
    *   `author_url` (*str*, optional): Profile link.
    *   `access_token` (*str*, optional): Access token of the Telegraph account (only returned by `createAccount` and `revokeAccessToken`).
    *   `auth_url` (*str*, optional): URL to authorize a browser on telegra.ph and connect it to a Telegraph account (valid for one use and 5 minutes only).
    *   `page_count` (*int*, optional): Number of pages belonging to the Telegraph account.

<a name="pagelist"></a>

### PageList

This object represents a list of Telegraph articles belonging to an account. Most recently created articles first.

*   **Fields:**

    *   `total_count` (*int*): Total number of pages belonging to the target Telegraph account.
    *   `pages` (*list[Page]*): Requested pages of the target Telegraph account.

<a name="page"></a>

### Page

This object represents a page on Telegraph.

*   **Fields:**

    *   `path` (*str*): Path to the page.
    *   `url` (*str*): URL of the page.
    *   `title` (*str*): Title of the page.
    *   `description` (*str*): Description of the page.
    *   `author_name` (*str*, optional): Name of the author, displayed below the title.
    *   `author_url` (*str*, optional): Profile link.
    *   `image_url` (*str*, optional): Image URL of the page.
    *   `content` (*list[Union[str, NodeElement]]*, optional): [Content](#content-format) of the page.
    *   `views` (*int*): Number of page views for the page.
    *   `can_edit` (*bool*, optional): `True` if the target Telegraph account can edit the page (only returned if `access_token` passed).

<a name="pageviews"></a>

### PageViews

This object represents the number of page views for a Telegraph article.

*   **Fields:**

    *   `views` (*int*): Number of page views for the target page.

<a name="node"></a>

### Node

This abstract object represents a DOM Node. It can be a *String* which represents a DOM text node or a [NodeElement](#nodeelement) object.

<a name="nodeelement"></a>

### NodeElement

This object represents a DOM element node.

*   **Fields:**

    *   `tag` (*str*): Name of the DOM element. Available tags: `a`, `aside`, `b`, `blockquote`, `br`, `code`, `em`, `figcaption`, `figure`, `h3`, `h4`, `hr`, `i`, `iframe`, `img`, `li`, `ol`, `p`, `pre`, `s`, `strong`, `u`, `ul`, `video`.
    *   `attrs` (*dict*, optional): Attributes of the DOM element. Key of object represents name of attribute, value represents value of attribute. Available attributes: `href`, `src`.
    *   `children` (*list[Node]*, optional): List of child nodes for the DOM element.

<a name="content-format"></a>

### Content Format

The Telegraph API uses a DOM-based format to represent the content of the page.  The `content` parameter in `createPage` and `editPage` expects a list of nodes, where each node can be either a string (representing text) or a `NodeElement` object.

Here's an example of how to create a simple page with a paragraph and a bolded text:

```python
import asyncio
import telegra

async def main():
    telegraph = telegra.Telegraph()
    try:
        account = await telegraph.createAccount(short_name="My Account")
        access_token = account.access_token

        content = [
            "This is a paragraph of text.",
            telegra.NodeElement(tag="b", children=["This is bold text."])
        ]
        page = await telegraph.createPage(
            access_token=access_token, title="My First Page", content=content
        )
        print(f"Page URL: {page.url}")
    except telegra.TelegraphError as e:
        print(f"Error: {e}")

    if __name__ == "__main__":
        asyncio.run(main())
```
