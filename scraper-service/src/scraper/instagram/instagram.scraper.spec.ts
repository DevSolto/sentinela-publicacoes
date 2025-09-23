import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { Test, TestingModule } from '@nestjs/testing';
import { AxiosResponse } from 'axios';
import { InstagramScraper } from './instagram.scraper';
import { InstagramConfig } from '../../config/instagram.config';
import { ScrapedPost } from '../interfaces/scraped-post.interface';

describe('InstagramScraper', () => {
  let scraper: InstagramScraper;
  let httpService: HttpService & { axiosRef: { get: jest.Mock } };
  const config: InstagramConfig = {
    baseUrl: 'https://api.instagram.test',
    headers: { 'User-Agent': 'jest' },
    defaultLimit: 5,
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        InstagramScraper,
        {
          provide: HttpService,
          useValue: { axiosRef: { get: jest.fn() } },
        },
        {
          provide: ConfigService,
          useValue: {
            get: jest.fn().mockReturnValue(config),
          },
        },
      ],
    }).compile();

    scraper = module.get(InstagramScraper);
    httpService = module.get(HttpService);
  });

  it('throws when username is missing', async () => {
    await expect(scraper.fetchLatestPosts('')).rejects.toThrow(
      'Instagram username is required',
    );
  });

  it('maps instagram response into posts', async () => {
    const response: AxiosResponse = {
      data: {
        data: {
          user: {
            edge_owner_to_timeline_media: {
              edges: [
                {
                  node: {
                    id: '123',
                    shortcode: 'abc',
                    display_url: 'https://example.com/img.jpg',
                    taken_at_timestamp: 1700000000,
                    is_video: false,
                    edge_liked_by: { count: 42 },
                    edge_media_to_comment: { count: 3 },
                    edge_media_to_caption: {
                      edges: [{ node: { text: 'caption' } }],
                    },
                  },
                },
              ],
            },
          },
        },
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {},
    };

    httpService.axiosRef.get.mockResolvedValue(response);

    const result = await scraper.fetchLatestPosts('account', 1);

    const expected: ScrapedPost[] = [
      {
        id: '123',
        shortcode: 'abc',
        caption: 'caption',
        imageUrl: 'https://example.com/img.jpg',
        takenAt: new Date(1700000000 * 1000).toISOString(),
        likeCount: 42,
        commentCount: 3,
        isVideo: false,
      },
    ];

    expect(result).toEqual(expected);
    expect(httpService.axiosRef.get).toHaveBeenCalledWith(config.baseUrl, {
      params: { username: 'account' },
      headers: config.headers,
    });
  });

  it('wraps axios errors into HttpException', async () => {
    const error = {
      isAxiosError: true,
      toJSON: () => ({}),
      message: 'Request failed',
      response: {
        status: 429,
        data: { message: 'Too many requests' },
      },
    };

    httpService.axiosRef.get.mockRejectedValue(error);

    await expect(scraper.fetchLatestPosts('account')).rejects.toMatchObject({
      status: 429,
      message: 'Too many requests',
    });
  });
});
