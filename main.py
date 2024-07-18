import asyncio
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from pydantic import BaseModel
from httpx import AsyncClient

app = FastAPI()
client = AsyncClient()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_API = "https://exercise.trunarrative.cloud/TruProxyAPI/rest/Companies/v1"


class CompaniesAndOfficersBody(BaseModel):
    companyName: str | None = None
    companyNumber: str | None = None


def get_query_param(body: CompaniesAndOfficersBody):
    match [body.companyName, body.companyNumber]:
        case [companyName, None]:
            return companyName
        case [None, companyNumber]:
            return companyNumber
        case [companyName, companyNumber]:
            return companyNumber
        case _:
            return None


async def get_officers_for_company(companyNumber: str, headers: dict[str, str]):
    officers_response = await client.get(
        f"{BASE_API}/Officers",
        params={"CompanyNumber": companyNumber},
        headers=headers,
    )

    officers = officers_response.json()

    if not "items" in officers:
        return []

    # only return the active officers
    return [officer for officer in officers["items"] if "resigned_on" not in officer]


@app.post("/")
async def companies_and_officers(
    # api key for the TruProxy API
    x_api_key: Annotated[str, Header()],
    body: CompaniesAndOfficersBody,
    # only send the active companies
    active_only: str | None = None,
):
    # set the correct query param based on the body passed
    query = get_query_param(body)
    if not query:
        raise HTTPException(status_code=400, detail="Invalid query param")

    # set the required header
    headers = {"x-api-key": x_api_key}

    companies_response = await client.get(
        f"{BASE_API}/Search", params={"Query": query}, headers=headers
    )

    companies = companies_response.json()

    # if there are no companies from the search
    if not "total_results" in companies:
        return []

    # only include active companies
    if active_only:
        companies["items"] = [
            company
            for company in companies["items"]
            if "company_status" in company and company["company_status"] == "active"
        ]

        companies["total_results"] = len(companies["items"])

    # fetch all officers for companies (parallel to fetch faster)
    officers = await asyncio.gather(
        *[
            get_officers_for_company(c["company_number"], headers)
            for c in companies["items"]
        ]
    )

    # map active officers to companies
    for index, c in enumerate(companies["items"]):
        c["officers"] = officers[index]

    return companies


@app.get("/company/{company_number}")
async def get_company(
    company_number: str,
    # api key for the TruProxy API
    x_api_key: Annotated[str, Header()],
):
    # set the required header
    headers = {"x-api-key": x_api_key}

    companies_response = await client.get(
        f"{BASE_API}/Search", params={"Query": company_number}, headers=headers
    )

    companies = companies_response.json()

    # if there are no companies from the search
    if not "total_results" in companies:
        return None

    # select the company with the company_number (always the first one)
    company = companies["items"][0]

    # fetch company officers
    officers = await get_officers_for_company(company["company_number"], headers)
    company["officers"] = officers

    return company
