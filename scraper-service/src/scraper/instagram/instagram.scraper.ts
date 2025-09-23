import { HttpService } from '@nestjs/axios';
import {
  BadRequestException,
  HttpException,
  HttpStatus,
  Injectable,
  Logger,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios, { type AxiosError } from 'axios';
import { InstagramConfig } from '../../config/instagram.config';
import { ScrapedPost } from '../interfaces/scraped-post.interface';

type InstagramEdge = {
  node: {
    id: string;
    shortcode: string;
    display_url: string;
    taken_at_timestamp: number;
    is_video: boolean;
    edge_liked_by?: { count: number };
    edge_media_to_comment?: { count: number };
    edge_media_to_caption?: {
      edges: Array<{ node: { text: string } }>;
    };
  };
};

type InstagramProfileResponse = {
  data?: {
    user?: {
      edge_owner_to_timeline_media?: {
        edges?: InstagramEdge[];
      };
    };
  };
  status?: string;
};

@Injectable()
export class InstagramScraper {
  private readonly logger = new Logger(InstagramScraper.name);

  constructor(
    private readonly httpService: HttpService,
    private readonly configService: ConfigService,
  ) {}

  async fetchLatestPosts(
    username: string,
    limit?: number,
  ): Promise<ScrapedPost[]> {
    if (!username || !username.trim()) {
      throw new BadRequestException('Instagram username is required');
    }

    const config = this.configService.get<InstagramConfig>('instagram');
    if (!config) {
      throw new Error('Instagram configuration is not available');
    }

    const fallbackLimit =
      Number.isFinite(config.defaultLimit) && config.defaultLimit > 0
        ? config.defaultLimit
        : 12;
    const normalizedLimit = limit ?? fallbackLimit;
    const effectiveLimit = Math.min(Math.max(normalizedLimit, 1), 50);

    try {
      const response =
        await this.httpService.axiosRef.get<InstagramProfileResponse>(
          config.baseUrl,
          {
            params: { username },
            headers: config.headers,
          },
        );

      const edges =
        response.data?.data?.user?.edge_owner_to_timeline_media?.edges ?? [];

      return edges.slice(0, effectiveLimit).map((edge) => ({
        id: edge.node.id,
        shortcode: edge.node.shortcode,
        caption:
          edge.node.edge_media_to_caption?.edges?.[0]?.node?.text ?? null,
        imageUrl: edge.node.display_url,
        takenAt: new Date(edge.node.taken_at_timestamp * 1000).toISOString(),
        likeCount: edge.node.edge_liked_by?.count ?? 0,
        commentCount: edge.node.edge_media_to_comment?.count ?? 0,
        isVideo: edge.node.is_video ?? false,
      }));
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<{ message?: string } | string>;
        const responseData = axiosError.response?.data;
        const details =
          (typeof responseData === 'string'
            ? responseData
            : responseData?.message) ?? axiosError.message;
        const statusCode =
          axiosError.response?.status ?? HttpStatus.BAD_GATEWAY;

        this.logger.error(
          `Failed to fetch Instagram posts for ${username}: ${details}`,
        );

        throw new HttpException(details, statusCode);
      }

      const message =
        error instanceof Error
          ? error.message
          : 'Unknown Instagram scraping error';
      this.logger.error(
        `Unexpected error while scraping Instagram for ${username}: ${message}`,
      );
      throw error instanceof Error ? error : new Error(message);
    }
  }
}
