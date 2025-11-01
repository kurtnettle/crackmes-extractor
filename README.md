# crackmes-extractor

A Python CLI tool to scrape, extract, and compile challenge data from [crackmes](https://crackmes.one/) into a structured JSON format.

## ⚠️ Responsible Scraping Notice

This tool includes built-in rate limiting and conservative intervals to respect `crackmes`'s servers. By using this software, you agree to the following terms:

- **Not to** modify the rate limiting intervals or bypass throttling mechanisms.
- **Not to** run multiple instances simultaneously.
- **Respectful** to the website's terms of service (if any).
- **Mindful** of server impact.

## Quickstart

### Using [uv](https://docs.astral.sh/uv/getting-started/installation/) (Recommended)

```bash
# uv will automatically install dependencies on first run
uv run scraper.py --dump-htmls --extract-challs
```

## Usage

To run, simply type in your terminal

```sh
python scraper.py --dump-htmls --extract-challs
```

## Commands

<table>
  <thead>
    <th>Command</th>
    <th>Description</th>
  </thead>
  <tbody>
    <tr>
      <td>
        <code>-d, --dump-htmls</code>
      </td>
      <td>Download HTML pages</td>
    </tr>
    <tr>
      <td>
        <code>-e, --extract-challs</code>
      </td>
      <td>Extract challenges from downloaded HTML</td>
    </tr>
  </tbody>
</table>

## Data Format

The generated `challs.json` includes:

```json
{
	"challs": [
		{
			"problem": {
				"name": "crackme1 by drakenza",
				"link": "/crackme/5ab77f6333c5d40ad448ca28"
			},
			"author": "crackmes.de",
			"lang": "C/C++",
			"arch": "x86",
			"difficulty": 5,
			"quality": 4,
			"platform": "Windows",
			"date": "2018-03-25T10:52:00+00:00",
			"writeups": 1,
			"comments": 0
		}
	],
	"last_updated": "2025-11-01T19:13:00.939042+00:00"
}
```

## 🤝 Contributing

Contributions are welcome! If you'd like to improve the tool or fix bugs, feel free to submit a pull request. Please ensure your changes align with the project's coding standards and include appropriate tests.

## 📜 License

This project is licensed under the GPLv3 License. See the [LICENSE](../LICENSE) file for full details.

By contributing to this project, you agree that your contributions will be licensed under the GPLv3 License as well.

## ⚖️ Liability

Maintainers assume no liability for damages resulting from misuse of this software and users are solely responsible for their consequences.
