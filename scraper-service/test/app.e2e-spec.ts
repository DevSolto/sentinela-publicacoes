import { ValidationPipe, INestApplication } from '@nestjs/common';
import { Test, TestingModule } from '@nestjs/testing';
import request from 'supertest';
import { App } from 'supertest/types';
import { AppModule } from './../src/app.module';
import { InstagramScraper } from '../src/scraper/instagram/instagram.scraper';
import { ScrapedPost } from '../src/scraper/interfaces/scraped-post.interface';

describe('Application (e2e)', () => {
  let app: INestApplication<App>;
  const samplePosts: ScrapedPost[] = [
    {
      id: '1',
      shortcode: 'short1',
      caption: 'Example post',
      imageUrl: 'https://example.com/image1.jpg',
      takenAt: new Date('2024-01-01T00:00:00Z').toISOString(),
      likeCount: 10,
      commentCount: 2,
      isVideo: false,
    },
  ];

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    })
      .overrideProvider(InstagramScraper)
      .useValue({ fetchLatestPosts: jest.fn().mockResolvedValue(samplePosts) })
      .compile();

    app = moduleFixture.createNestApplication();
    app.setGlobalPrefix('api');
    app.useGlobalPipes(
      new ValidationPipe({
        transform: true,
        whitelist: true,
        forbidNonWhitelisted: true,
      }),
    );
    await app.init();
  });

  afterEach(async () => {
    await app.close();
  });

  it('/api/health (GET)', async () => {
    const response = await request(app.getHttpServer()).get('/api/health');

    expect(response.status).toBe(200);
    expect(response.body).toEqual({ status: 'ok' });
  });

  it('/api/scraper/instagram/:username/posts (GET)', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/scraper/instagram/test-user/posts')
      .query({ limit: 1 });

    expect(response.status).toBe(200);
    expect(response.body).toEqual(samplePosts);
  });

  it('rejects invalid query parameters', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/scraper/instagram/test-user/posts')
      .query({ limit: 'invalid' });

    expect(response.status).toBe(400);
  });
});
