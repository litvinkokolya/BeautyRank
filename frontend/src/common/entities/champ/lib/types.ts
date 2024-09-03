export interface IMemberNomination {
  id: number;
  nomination: string;
  nomination_info: any;
  category: string;
  member: string;
  result_sum: number;
  is_done: boolean;
}

export interface ICategoryNomination {
  event_category: number;
  nomination: number;
  member_nomination: IMemberNomination[];
}

export interface IChamp {
  id: number;
  name: string;
  image: string;
  finished: boolean;
  role: string;
}

export interface ChampCardProps {
  champ: IChamp;
  disableChamp: boolean;
}

export interface IChampNominationsWinners {
  category: string;
  nominations: Array<{
    nomination: string;
    members:  Array<{
      member: string;
      result_all: number;
    }>;
  }>;
}

export interface IChampCategoriesWinners {
  name: string;
  members: Array<{
    member: string;
    result_all: number;
  }>;
}
