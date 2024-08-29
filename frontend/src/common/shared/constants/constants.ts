export const getUserRole = (role: string): boolean | undefined => {
  if (
    typeof window !== 'undefined' &&
    window.localStorage &&
    localStorage.getItem('champ')
  ) {
    return JSON.parse(localStorage.getItem('champ')!)?.role === role;
  }
};

export const getUserIsStaff = (): boolean | undefined => getUserRole('Судья');
export const getUserIsMaster = (): boolean | undefined => getUserRole('Участник');
export const getUserIsOrganizer = (): boolean | undefined =>
  getUserRole('Организатор');

export const USER_IS_UNKNOWN = 'Unknown role';
