const { createClient } = require('redis');

const redisUrl = process.env.REDIS_URL;

let redisClient = null;
let redisConnectPromise = null;

const isRedisEnabled = () => Boolean(redisUrl);

const getRedisClient = () => {
	if (!isRedisEnabled()) {
		return null;
	}

	if (!redisClient) {
		redisClient = createClient({ url: redisUrl });

		redisClient.on('error', (error) => {
			console.error('Redis client error:', error);
		});
	}

	return redisClient;
};

const connectRedis = async () => {
	const client = getRedisClient();

	if (!client) {
		return null;
	}

	if (client.isOpen) {
		return client;
	}

	if (!redisConnectPromise) {
		redisConnectPromise = client.connect().catch((error) => {
			console.error('Redis connection failed:', error);
			return null;
		}).finally(() => {
			redisConnectPromise = null;
		});
	}

	return redisConnectPromise;
};

const getCachedJson = async (key) => {
	const client = await connectRedis();

	if (!client) {
		return null;
	}

	try {
		const value = await client.get(key);
		return value ? JSON.parse(value) : null;
	}
	catch (error) {
		console.error(`Redis get failed for ${key}:`, error);
		return null;
	}
};

const setCachedJson = async (key, value, ttlSeconds) => {
	const client = await connectRedis();

	if (!client) {
		return false;
	}

	try {
		await client.set(key, JSON.stringify(value), {
			EX: ttlSeconds,
		});

		return true;
	}
	catch (error) {
		console.error(`Redis set failed for ${key}:`, error);
		return false;
	}
};

const deleteByPattern = async (pattern) => {
	const client = await connectRedis();

	if (!client) {
		return 0;
	}

	try {
		const keys = [];
		for await (const key of client.scanIterator({ MATCH: pattern, COUNT: 100 })) {
			keys.push(key);
		}

		if (!keys.length) {
			return 0;
		}

		await client.del(keys);
		return keys.length;
	}
	catch (error) {
		console.error(`Redis delete failed for pattern ${pattern}:`, error);
		return 0;
	}
};

module.exports = {
	connectRedis,
	getRedisClient,
	getCachedJson,
	setCachedJson,
	deleteByPattern,
};