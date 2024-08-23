export interface IMember {
  id: number;
  nomination: string;
  nomination_info: {
    after: [
      {
        id: number;
        name: string;
        image: string;
      }
    ];
    before: [
      {
        id: number;
        name: string;
        image: string;
      }
    ];
  };
  category: string;
  member: string;
  result_sum: number;
  is_done: boolean;
  preview: string;
  url_message_video: string;
  id_member: number;
}

export interface ResultsFromPaginator{
  count: number,
  next: string | null,
  previous: string | null,
  results: IMember[]
}

export interface MemberCardProps {
  member: IMember;
}
