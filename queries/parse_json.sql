SELECT
    json_extract(baseToken, '$.address') AS baseToken_address,
    json_extract(baseToken, '$.name') AS baseToken_name,
    json_extract(baseToken, '$.symbol') AS baseToken_symbol,
	chainId,
	dexId,
	json_extract(liquidity, '$.usd') AS liquidity_usd,
	marketCap,
	pairAddress,
	pairCreatedAt,
	datetime(pairCreatedAt/1000, 'unixepoch') AS pairCreatedAt_dt,
	priceUsd,
	json_extract(quoteToken, '$.address') AS quoteToken_address,
	json_extract(quoteToken, '$.name') AS quoteToken_name,
	json_extract(quoteToken, '$.symbol') AS quoteToken_symbol,
	json_extract(volume, '$.h24') AS volume_h24
FROM DexScreener_L1;