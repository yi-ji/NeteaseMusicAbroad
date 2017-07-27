function FindProxyForURL(url, host) {
	// return "PROXY localhost:32794";

	// our local URLs from the domains below example.com don't need a proxy:
	if (isInNet(host, dnsResolve("music.163.com"), "255.255.255.255"))
	{
		// if (shExpMatch(url, "https://*"))
		// {
		// 	//return "DIRECT";
		// 	return "PROXY localhost:32796";
		// }
		return "PROXY localhost:32794";
	}

	// All other requests go through port 8080 of proxy.example.com.
	// should that fail to respond, go directly to the WWW:
	return "DIRECT";
}