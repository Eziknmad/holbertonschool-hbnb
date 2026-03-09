"""Persistence layer package."""
from app.persistence.repository import Repository, InMemoryRepository

__all__ = ['Repository', 'InMemoryRepository']
