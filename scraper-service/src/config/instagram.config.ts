import { registerAs } from '@nestjs/config';

export interface InstagramConfig {
  baseUrl: string;
  headers: Record<string, string>;
  defaultLimit: number;
}

function parseHeaders(rawHeaders?: string): Record<string, string> {
  if (!rawHeaders) {
    return {};
  }

  try {
    const parsed = JSON.parse(rawHeaders) as unknown;
    if (
      typeof parsed !== 'object' ||
      parsed === null ||
      Array.isArray(parsed)
    ) {
      throw new Error('INSTAGRAM_HEADERS must be a JSON object string');
    }

    return Object.entries(parsed as Record<string, unknown>).reduce<
      Record<string, string>
    >((acc, [key, value]) => {
      if (typeof value === 'string') {
        acc[key] = value;
      }

      return acc;
    }, {});
  } catch (error: unknown) {
    const message =
      error instanceof Error ? error.message : 'Unknown headers parsing error';
    throw new Error(`Failed to parse INSTAGRAM_HEADERS: ${message}`);
  }
}

export default registerAs<InstagramConfig>('instagram', () => {
  const headers: Record<string, string> = {
    'User-Agent':
      process.env.INSTAGRAM_USER_AGENT ??
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36',
    ...parseHeaders(process.env.INSTAGRAM_HEADERS),
  };

  if (process.env.INSTAGRAM_SESSION_ID) {
    headers.Cookie = `sessionid=${process.env.INSTAGRAM_SESSION_ID}`;
  }

  return {
    baseUrl:
      process.env.INSTAGRAM_BASE_URL ??
      'https://www.instagram.com/api/v1/users/web_profile_info/',
    headers,
    defaultLimit: Number(process.env.INSTAGRAM_DEFAULT_LIMIT ?? 12),
  };
});
