from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class FeeType(str, Enum):
    MANAGEMENT_FEE = "MANAGEMENT_FEE"
    CARRIED_INTEREST = "CARRIED_INTEREST"
    ORGANIZATIONAL_EXPENSES = "ORGANIZATIONAL_EXPENSES"
    TRANSACTION_FEE_OFFSET = "TRANSACTION_FEE_OFFSET"
    OTHER = "OTHER"


class FundPhase(str, Enum):
    INVESTMENT_PERIOD = "INVESTMENT_PERIOD"
    POST_INVESTMENT_PERIOD = "POST_INVESTMENT_PERIOD"
    EXTENSION_PERIOD = "EXTENSION_PERIOD"
    ENTIRE_TERM = "ENTIRE_TERM"


class CalculationBasis(str, Enum):
    COMMITTED_CAPITAL = "COMMITTED_CAPITAL"
    INVESTED_CAPITAL = "INVESTED_CAPITAL"
    NET_INVESTED_CAPITAL = "NET_INVESTED_CAPITAL"
    NET_ASSET_VALUE = "NET_ASSET_VALUE"
    COST_BASIS = "COST_BASIS"
    OTHER = "OTHER"


class WaterfallType(str, Enum):
    WHOLE_OF_FUND = "WHOLE_OF_FUND"  # European style
    DEAL_BY_DEAL = "DEAL_BY_DEAL"  # American style



class FeeEntry(BaseModel):
    fee_type: FeeType = Field(..., description="The formal category of the fee.")
    phase: FundPhase = Field(
        default=FundPhase.ENTIRE_TERM,
        description="The applicable lifecycle period of the fund.",
    )
    rate_percentage: Optional[float] = Field(
        None,
        description="Annual rate as an absolute percentage number (e.g., 2.0 for 2.0%, 0.25 for 25 bps).",
    )
    calculation_basis: Optional[CalculationBasis] = Field(
        None,
        description="The base capital amount upon which the percentage fee is calculated.",
    )
    hurdle_rate_percentage: Optional[float] = Field(
        None,
        description="Preferred return/hurdle rate applicable to carried interest (e.g., 8.0).",
    )
    waterfall_type: Optional[WaterfallType] = Field(
        None,
        description="Distribution waterfall style if carried interest is detected.",
    )
    fee_cap_amount: Optional[float] = Field(
        None,
        description="Fixed currency cap if explicitly specified (e.g., for organizational expenses).",
    )
    source_clause: Optional[str] = Field(
        None,
        description="The section or exact sentence reference from the source agreement.",
    )
    raw_text_citation: Optional[str] = Field(
        None,
        description="The exact verbatim sentence excerpt from the LPA document where this information is found.",
    )


class FundFeeSchedule(BaseModel):
    fund_name: Optional[str] = Field(
        None, description="Name of the venture fund entity."
    )
    fees: List[FeeEntry] = Field(
        ...,
        description="Structured list of all identified fee types, rates, and step-downs.",
    )
