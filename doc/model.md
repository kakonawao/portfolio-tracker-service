# Model

This document details the model to be used for the service.

## Auth

The data within the service can be split into two groups:

* global: visible to all users, mostly static
* assets: owned by users, mostly dynamic

Global objects provide the foundation used to create user-owned assets, so they must be visible to all users but managed
by administrators only. They include institutions (banks), financial instruments (currencies, stocks) and their quotes. 

Assets are the actual values of the global instruments owned by the users, such as bank account balances and stocks 
owned. They must be domain-restricted to the owners, invisible to any other user without exception (including 
administrators).

```yaml
User:
  username: string
  hashed_password: string
  is_admin: boolean
  base_currency: Currency
```

## Global

Financial institutions are only used for information purposes, and can all be expressed with a single object.

```yaml
Institution:
  name: string
  code: string
  type: [bank, broker, exchange]
```

Financial instruments can also be of different types but in their case they can be heterogeneous, so they must be split
in different subtypes. They hold the their values in time.

```yaml
Instrument:
  description: string
  symbol: string
  type: choice[currency, index, security]
  values: map(date, InstrumentValue)

InstrumentValue:
  instrument: Instrument
  value: decimal
  
Currency(Instrument):
  ..
  
Index(Instrument):
  ..

Security(Instrument):
  ..
  exchange: Institution(type=exchange)
```

## Assets

Assets are grouped into accounts.

```yaml
Account:
  owner: User
  type: choice[current, savings, loan]
  holder: Institution(type=[bank, broker])
  name: string
  code: string
  assets: list[Asset]

AccountAsset:
  instrument: Instrument
  quantity: decimal
```

Assets values must be modified using transactions. A transaction has a "value", which *should* be the equivalent to the 
sum of its credits (and debits). However, due to the complexity of managing the different exchange rates used by 
institutions I see no easy way to validate the ledger change, except counting any difference as a gain or cost.

```yaml
Transaction:
  category: choice
  entries: list[TransactionEntry]
  value: Value

TransactionEntry:
  type: choice[debit, credit]
  account: Account
  instrument: Instrument
  quantity: decimal
```
