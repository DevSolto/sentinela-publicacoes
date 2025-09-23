import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { InstagramScraper } from './instagram/instagram.scraper';
import { ScraperController } from './scraper.controller';
import { ScraperService } from './scraper.service';

@Module({
  imports: [
    HttpModule.register({
      timeout: 10000,
      maxRedirects: 3,
    }),
  ],
  controllers: [ScraperController],
  providers: [InstagramScraper, ScraperService],
  exports: [ScraperService],
})
export class ScraperModule {}
