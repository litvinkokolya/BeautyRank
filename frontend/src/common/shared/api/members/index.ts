import {IMember, ResultsFromPaginator} from 'common/entities/member';
import { ENDPOINTS } from '../endpoints';
import { axiosInstanse } from '../instanse';
import { AxiosPromise } from 'axios';
import { IPhoto } from 'common/features/upload-member-photo/model';

export const getMembers = (champId: number, page: number, pageSize: number, isDone: boolean): AxiosPromise<ResultsFromPaginator> =>
  axiosInstanse.get(
    ENDPOINTS.MEMBERS.MEMBERS +
      `?category_nomination__event_category__event=${champId}&page=${page}&page_size=${pageSize}&is_done=${isDone}`
  );

export const getMember = (memberId: number): AxiosPromise<IMember> =>
  axiosInstanse.get(ENDPOINTS.MEMBERS.MEMBERS + memberId + '/');

export const getMemberPhotos = (memberId: number): AxiosPromise<IPhoto[]> =>
  axiosInstanse.get(
    ENDPOINTS.MEMBERS.PHOTOS + '?member_nomination=' + memberId
  );

export const setMemberPhotos = (data: FormData) =>
  axiosInstanse.post(ENDPOINTS.MEMBERS.PHOTOS, data);
