# Model

The data within the service can be split into three groups:

* auth: system users
* global: static objects used to define assets
* assets: dynamic objects owned by users


## Auth

Common ownership of assets (eg, multi-user accounts) is not a requirement, we only need a single User object to manage
both authentication and assets ownership. Concerning operation permissions, the only distinction we can make is whether
the user can modify global objects or not (eg, administrator).

### User

The user must have an *administrator* flag and a base currency to calculate assets total values.

```yaml
User:
  username: string
  hashed_password: string
  is_admin: boolean
  base_currency: Currency
```

## Global

Global objects provide the foundation used to create user-owned assets, and include institutions (banks), financial 
instruments (currencies, stocks) and their quotes. They must be visible by all users, but managed only by 
administrators.

### Institution

Financial institutions are only used for information purposes, and can all be expressed with a single object.

```yaml
Institution:
  name: string
  code: string
  type: [bank, broker, exchange]
```

### Instrument

Financial instruments can also be of different types, but the only subclass we need to differentiate is Security because
it has an extra field (exchange). The attribute code must not be input (only as resource identifier), it must be 
calculated based on the instrument symbol and its exchange (if any).

```yaml
Instrument:
  description: string
  symbol: string
  code: string
  type: choice[currency, index, security]
 
Security(Instrument):
  ..
  type: security
  exchange: Institution(type=exchange)

```

### Values

Instrument values (currency rates, security quotes) need to be tracked by time, and they're given in *another 
instrument*, probably always a currency.
I am still deciding how to do this, but the following model could work.

```yaml
InstrumentValue:
  date: date
  instrument: Instrument
  currency: Instrument(type=currency)
  value: decimal
```

Optionally, we could include these nested inside the instrument documents, but they'll probably get too large.


## Assets

Assets are the actual values of the global instruments owned by the users. They and must be domain-restricted to the 
owners, invisible to any other user without exception (including administrators).

### Account

Accounts are the containers for user assets.

```yaml
Account:
  owner: str
  type: choice[current, savings, investment, null]
  holder: Institution(type=[bank, broker])
  name: string
  code: string
  assets: list[Asset]

Asset:
  instrument: Instrument
  quantity: decimal
```

### Transaction

A transaction is used to modify the assets, and it has a "value" that should be the equivalent to the sum of its credits 
(and debits).

```yaml
Transaction:
  category: choice
  entries: list[Entry]
  value: Value

Entry:
  type: choice[debit, credit]
  account: Account
  instrument: Instrument
  quantity: decimal
```
