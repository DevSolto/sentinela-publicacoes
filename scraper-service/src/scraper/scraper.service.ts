import { Injectable } from '@nestjs/common';
import { InstagramScraper } from './instagram/instagram.scraper';
import { ScrapedPost } from './interfaces/scraped-post.interface';

@Injectable()
export class ScraperService {
  constructor(private readonly instagramScraper: InstagramScraper) {}

  async scrapeInstagram(
    username: string,
    limit?: number,
  ): Promise<ScrapedPost[]> {
    return this.instagramScraper.fetchLatestPosts(username, limit);
  }
}
