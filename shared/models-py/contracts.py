"""Shared Pydantic models for NIRIX Diagnostics.

These mirror the JSON schemas under shared/api-contracts/schemas.
Backend and tools can import from here to stay in sync.
"""

from pydantic import BaseModel
from typing import Optional, List, Any


class AuthUser(BaseModel):
    id: int
    email: str
    name: str


class Vehicle(BaseModel):
    id: int
    name: str
    code: str


class TestDefinition(BaseModel):
    id: int
    name: str
    identifier: str
    test_type: str
    vehicle_id: int


class LogEntry(BaseModel):
    id: int
    vehicle_id: int
    test_id: int
    status: str
    message: str


class VersionInfo(BaseModel):
    id: int
    version: str
    vehicle_id: int
