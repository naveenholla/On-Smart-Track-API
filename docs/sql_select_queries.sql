SELECT * FROM public.admin_lookup_marketexchange;
SELECT * FROM public.admin_lookup_marketdaytype;
SELECT * FROM public.admin_lookup_marketdaycategory;
SELECT * FROM public.admin_lookup_marketdays order by date, category_id
SELECT * FROM public.admin_lookup_marketdays where category_id = 4
SELECT * FROM public.market_data_equities
SELECT * FROM public.market_data_indices
SELECT * FROM public.market_data_equitiesindices