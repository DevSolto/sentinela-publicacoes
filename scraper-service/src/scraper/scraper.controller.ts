import { Controller, Get, Param, Query } from '@nestjs/common';
import { InstagramFeedQueryDto } from './dto/instagram-feed-query.dto';
import { ScrapedPost } from './interfaces/scraped-post.interface';
import { ScraperService } from './scraper.service';

@Controller('scraper')
export class ScraperController {
  constructor(private readonly scraperService: ScraperService) {}

  @Get('instagram/:username/posts')
  getInstagramPosts(
    @Param('username') username: string,
    @Query() query: InstagramFeedQueryDto,
  ): Promise<ScrapedPost[]> {
    return this.scraperService.scrapeInstagram(username, query.limit);
  }
}
