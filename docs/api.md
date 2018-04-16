# API

CALC's back end exposes a public API for its labor rates data. This API is used by CALC's front end Data Explorer application, and can also be accessed by any third-party application over the public internet.

## API endpoints

The following documentation assumes you're trying to access the API from the production instance via a tool like `curl` at `https://calc.gsa.gov/api/`.
In development, use `http://localhost:8000/api/`.

### `/rates/`

You can access labor rate information at `/rates/`.

```
https://calc.gsa.gov/api/rates/
```

#### Labor Categories

You can search for prices of specific labor categories by using the `q` parameter. For example:

```
https://calc.gsa.gov/api/rates/?q=accountant
```

You can change the way that labor categories are searched by using the `query_type` parameter, which can be either:

* `match_all` (the default), which matches all words in the query;
* `match_phrase`, which matches the query as a phrase; or
* `match_exact`, which matches labor categories exactly

You can search for multiple labor categories separated by a comma.

```
https://calc.gsa.gov/api/rates/?q=trainer,instructor
```

If any of the labor categories you'd like included in your search has a comma, you can surround that labor category with quotation marks:

```
https://calc.gsa.gov/api/rates/?q="engineer, senior",instructor
```

All of the query types are case-insensitive.

#### Education and Experience Filters

##### Experience

You can also filter by the minimum years of experience and maximum years of experience. For example:

```
https://calc.gsa.gov/api/rates/?&min_experience=5&max_experience=10&q=technical
```

Or, you can filter with a single, comma-separated range.
For example, if you wanted results with more than five years and less than ten years of experience:

```
https://calc.gsa.gov/api/rates/?experience_range=5,10
```

##### Education

There are two ways to filter based on education: `min_education` and `education`.

These filters accept one or more (comma-separated) education values:

* `HS` (high school),
* `AA` (associates),
* `BA` (bachelors),
* `MA` (masters), and
* `PHD` (Ph.D).

```
https://calc.gsa.gov/api/rates/?education=AA,BA
```

Use `min_education` to get all results that meet and exceed the selected education.
The following example will return results that have an education level of `MA` or `PHD`:

```
https://calc.gsa.gov/api/rates/?min_education=MA
```

The default pagination is set to 200. You can paginate using the `page` parameter:

```
https://calc.gsa.gov/api/rates/?q=translator&page=2
```

#### Price Filters

You can filter by price with any of the `price` (exact match), `price__lte` (price is less than or equal to) or `price__gte` (price is greater than or equal to) parameters:

```
https://calc.gsa.gov/api/rates/?price=95
https://calc.gsa.gov/api/rates/?price__lte=95
https://calc.gsa.gov/api/rates/?price__gte=95
```

The `price__lte` and `price__gte` parameters may be used together to search for a price range:

```
https://calc.gsa.gov/api/rates/?price__gte=95&price__lte=105
```

#### Excluding Records

You can also exclude specific records from the results by passing in an `exclude` parameter and a comma-separated list of ids:

```
https://calc.gsa.gov/api/rates/?q=environmental+technician&exclude=875173,875749
```

#### Other Filters

Other parameters allow you to filter by:

* The contract schedule of the transaction.
* The contract SIN of the transaction.
* Whether or not the vendor is a small business (valid values: `s` [small] and `o` [other]).
* Whether or not the vendor works on the contractor or customer site.

Here is an example with all four parameters (`schedule`, `sin`, `site`, and `business_size`) included:

```
https://calc.gsa.gov/api/rates/?schedule=mobis&sin=874&site=customer&business_size=s
```

For schedules, there are 8 different values that will return results (case-insensitive):

* Environmental
* AIMS
* Logistics
* Language Services
* PES
* MOBIS
* Consolidated
* IT Schedule 70

For SIN codes, there are several possible codes. They will contain the following numbers for their corresponding schedules:

* 899 - Environmental
* 541 - AIMS
* 87405 - Logistics
* 73802 - Language Services
* 871 - PES
* 874 - MOBIS
* 132 - IT Schedule 70

For site, there are three values (also case-insensitive):

* customer
* contractor
* both

And the `small_business` parameter can be either `s` for small business, or `o` for other than small business.
