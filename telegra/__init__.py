import asyncio
import json
from typing import Any, Dict, List, Optional, Union

import aiohttp
import attrs
from attrs import define, field, validators
from attrs.validators import instance_of

from yarl import URL

API_URL = "https://api.telegra.ph"

ALLOWED_TAGS = {
    "a", "aside", "b", "blockquote", "br", "code", "em", "figcaption", "figure",
    "h3", "h4", "hr", "i", "iframe", "img", "li", "ol", "p", "pre", "s",
    "strong", "u", "ul", "video"
}


def length(min=None, max=None):
    """Validator that the length of the attribute is between min and max."""
    if min is None and max is None:
        raise ValueError("At least min or max must be specified.")

    def validate(instance, attribute, value):
        if value is None:
            return

        if not isinstance(value, str):
            raise TypeError(
                f"The attribute {attribute.name} must be a string "
                f"(got {value!r} that is a {type(value)})."
            )
        if min is not None and len(value) < min:
            raise ValueError(
                f"The attribute {attribute.name} length must be at least "
                f"{min} (got {len(value)})."
            )
        if max is not None and len(value) > max:
            raise ValueError(
                f"The attribute {attribute.name} length must be at most "
                f"{max} (got {len(value)})."
            )

    return validate


@define
class TelegraphResult:
    ok: bool = field()
    result: Optional[Dict[str, Any]] = field(default=None)
    error: Optional[str] = field(default=None)


@define
class Account:
    short_name: str = field(
        validator=[instance_of(str), length(min=1, max=32)]
    )
    author_name: Optional[str] = field(
        default=None,
        validator=attrs.validators.optional(validator=length(max=128)),
    )
    author_url: Optional[str] = field(
        default=None,
        validator=attrs.validators.optional(validator=length(max=512)),
    )
    access_token: Optional[str] = field(default=None)
    auth_url: Optional[str] = field(default=None)
    page_count: Optional[int] = field(default=None)


@define
class NodeElement:
    tag: str = field(validator=[instance_of(str), validators.in_(ALLOWED_TAGS)])
    attrs: Optional[Dict[str, str]] = field(default=None)
    children: Optional[List[Union[str, "NodeElement"]]] = field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"tag": self.tag}
        if self.attrs:
            result["attrs"] = self.attrs
        if self.children:
            result["children"] = [
                child if isinstance(child, str) else child.to_dict()
                for child in self.children
            ]
        return result


@define
class Page:
    path: str = field(validator=instance_of(str))
    url: str = field(validator=instance_of(str))
    title: str = field(validator=instance_of(str))
    description: str = field(validator=instance_of(str))
    author_name: Optional[str] = field(default=None)
    author_url: Optional[str] = field(default=None)
    image_url: Optional[str] = field(default=None)
    content: Optional[List[Union[str, NodeElement]]] = field(default=None)
    views: Optional[int] = field(default=None)
    can_edit: Optional[bool] = field(default=None)


@define
class PageList:
    total_count: int = field(validator=instance_of(int))
    pages: List[Page] = field()


@define
class PageViews:
    views: int = field(validator=instance_of(int))


class TelegraphError(Exception):
    pass


class Telegraph:
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self._session = session
        self.account: Optional[Account] = None

    async def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> TelegraphResult:
        url = URL(API_URL) / path
        session = self._session or aiohttp.ClientSession()
        try:
            async with session.post(str(url), data=data) as resp:
                resp.raise_for_status()
                result = await resp.json()

            if not result["ok"]:
                raise TelegraphError(result["error"])

            return TelegraphResult(**result)
        except Exception as e:
            raise
        finally:
            if self._session is None:
                await session.close()

    async def createAccount(
        self,
        short_name: str,
        author_name: Optional[str] = None,
        author_url: Optional[str] = None,
    ) -> Account:
        """Creates a new Telegraph account."""
        data = {"short_name": short_name}
        if author_name:
            data["author_name"] = author_name
        if author_url:
            data["author_url"] = author_url

        response = await self._request("POST", "createAccount", data=data)
        self.account = Account(**response.result)
        return self.account

    async def editAccountInfo(
        self,
        access_token: str,
        short_name: Optional[str] = None,
        author_name: Optional[str] = None,
        author_url: Optional[str] = None,
    ) -> Account:
        """Updates information about a Telegraph account."""
        data = {"access_token": access_token}
        if short_name:
            data["short_name"] = short_name
        if author_name:
            data["author_name"] = author_name
        if author_url:
            data["author_url"] = author_url

        response = await self._request("POST", "editAccountInfo", data=data)
        if response.result:
            self.account = attrs.evolve(self.account, **response.result)
        return self.account

    async def getAccountInfo(
        self, access_token: str, fields: Optional[List[str]] = None
    ) -> Account:
        """Gets information about a Telegraph account."""
        data = {"access_token": access_token}
        if fields:
            data["fields"] = json.dumps(fields)

        response = await self._request("POST", "getAccountInfo", data=data)
        if response.result:
            self.account = attrs.evolve(self.account, **response.result)
        return self.account

    async def revokeAccessToken(self, access_token: str) -> Account:
        """Revokes access_token and generate a new one."""
        data = {"access_token": access_token}
        response = await self._request("POST", "revokeAccessToken", data=data)
        if response.result:
            self.account = attrs.evolve(self.account, access_token=response.result.get("access_token"), auth_url=response.result.get("auth_url"))
        return self.account

    async def createPage(
        self,
        access_token: str,
        title: str,
        content: List[Union[str, NodeElement]],
        author_name: Optional[str] = None,
        author_url: Optional[str] = None,
        return_content: bool = False,
    ) -> Page:
        """Creates a new Telegraph page."""
        if not 1 <= len(title) <= 256:
            raise ValueError("Title must be between 1 and 256 characters")

        data = {
            "access_token": access_token,
            "title": title,
            "content": json.dumps([
                node if isinstance(node, str) else node.to_dict()
                for node in content
            ]),
            "return_content": str(return_content).lower(),
        }
        if author_name:
            if not 0 <= len(author_name) <= 128:
                raise ValueError("Author name must be between 0 and 128 characters")
            data["author_name"] = author_name
        if author_url:
            if not 0 <= len(author_url) <= 512:
                raise ValueError("Author URL must be between 0 and 512 characters")
            data["author_url"] = author_url

        response = await self._request("POST", "createPage", data=data)
        return Page(**response.result)

    async def editPage(
        self,
        access_token: str,
        path: str,
        title: str,
        content: List[Union[str, NodeElement]],
        author_name: Optional[str] = None,
        author_url: Optional[str] = None,
        return_content: bool = False,
    ) -> Page:
        """Edits an existing Telegraph page."""
        if not 1 <= len(title) <= 256:
            raise ValueError("Title must be between 1 and 256 characters")

        data = {
            "access_token": access_token,
            "path": path,
            "title": title,
            "content": json.dumps([
                node if isinstance(node, str) else node.to_dict()
                for node in content
            ]),
            "return_content": str(return_content).lower(),
        }
        if author_name:
            if not 0 <= len(author_name) <= 128:
                raise ValueError("Author name must be between 0 and 128 characters")
            data["author_name"] = author_name
        if author_url:
            if not 0 <= len(author_url) <= 512:
                raise ValueError("Author URL must be between 0 and 512 characters")
            data["author_url"] = author_url

        response = await self._request("POST", f"editPage/{path}", data=data)
        return Page(**response.result)

    async def getPage(self, path: str, return_content: bool = False) -> Page:
        """Gets a Telegraph page."""
        data = {"return_content": str(return_content).lower()}
        response = await self._request("POST", f"getPage/{path}", data=data)
        return Page(**response.result)

    async def getPageList(
        self, access_token: str, offset: int = 0, limit: int = 50
    ) -> PageList:
        """Gets a list of pages belonging to a Telegraph account."""
        if not 0 <= offset:
            raise ValueError("Offset must be a non-negative integer")
        if not 0 <= limit <= 200:
            raise ValueError("Limit must be between 0 and 200")

        data = {"access_token": access_token, "offset": str(offset), "limit": str(limit)}
        response = await self._request("POST", "getPageList", data=data)
        response.result["pages"] = [Page(**page) for page in response.result["pages"]]
        return PageList(**response.result)

    async def getViews(
        self,
        path: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None,
    ) -> PageViews:
        """Gets the number of views for a Telegraph article."""
        data: Dict[str, str] = {}
        if year:
            if not 2000 <= year <= 2100:
                raise ValueError("Year must be between 2000 and 2100")
            data["year"] = str(year)
        if month:
            if not 1 <= month <= 12:
                raise ValueError("Month must be between 1 and 12")
            data["month"] = str(month)
        if day:
            if not 1 <= day <= 31:
                raise ValueError("Day must be between 1 and 31")
            data["day"] = str(day)
        if hour:
            if not 0 <= hour <= 24:
                raise ValueError("Hour must be between 0 and 24")
            data["hour"] = str(hour)

        response = await self._request("POST", f"getViews/{path}", data=data)
        return PageViews(**response.result)


__all__ = [
    "Telegraph",
    "TelegraphResult",
    "Account",
    "NodeElement",
    "Page",
    "PageList",
    "PageViews",
    "TelegraphError",
              ]
