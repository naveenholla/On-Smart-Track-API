SELECT * FROM public.market_exchange;
SELECT * FROM public.market_marketdaytype;
SELECT * FROM public.market_marketdaycategory;
SELECT * FROM public.market_marketdaycategory_daytype;
SELECT * FROM public.market_marketday;

SELECT md.id, mdt.name, mdc.display_name, md.description, md.date, md.day, md.is_working_day, md.start_time, md.end_time FROM public.market_marketday md 
INNER JOIN public.market_marketdaycategory mdc ON md.category_id = mdc.id 
INNER JOIN public.market_marketdaytype mdt ON md.daytype_id = mdt.id
WHERE mdt.name = 'Trading Holidays'
AND mdc.display_name = 'Equities'
ORDER BY md.date

SELECT * FROM public.market_equity;
SELECT * FROM public.market_index;
SELECT * FROM public.market_equityindex ORDER BY sector, equity_id, index_id;
SELECT index_id, sum(equity_weightage) FROM public.market_equityindex group by index_id

SELECT * FROM public.market_equityendofday
SELECT * FROM public.market_equityendofdaycalcutated
SELECT * FROM public.market_equityderivativeendofday

SELECT * FROM public.market_indexendofday
SELECT * FROM public.market_indexderivativeendofday

SELECT * FROM public.market_equitylivedata
SELECT * FROM public.market_equitylivefuture
SELECT * FROM public.market_equityliveopeninterest
SELECT * FROM public.market_equityliveoptionchain

SELECT * FROM public.market_indexlivedata
SELECT * FROM public.market_indexlivefuture
SELECT * FROM public.market_indexliveopeninterest
SELECT * FROM public.market_indexliveoptionchain


